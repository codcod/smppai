"""
High-level SMPP client API

A thin layer over SMPPClient: connect and bind in one step, send text
without picking a data coding, and iterate decoded, reassembled inbound
messages with parsed delivery receipts.

    async with smpp.connect('localhost', 2775, 'user', 'secret') as client:
        result = await client.send('+306900000000', 'Hello!', receipt=True)
        async for msg in client.messages():
            print(msg.sender.addr, msg.text, msg.receipt)
"""

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import AsyncIterator, Dict, Literal, Optional, Tuple, Union

from ..exceptions import SMPPPDUException, SMPPValidationException
from ..gsm import UDH, ConcatenatedSMSHeader, MessagePart, reassemble_parts
from ..protocol import (
    DataCoding,
    DataSm,
    DeliverSm,
    MessageState,
    NpiType,
    OptionalTag,
    RegisteredDelivery,
    TonType,
)
from ..protocol.codec import decode_message_with_encoding, encode_message_with_encoding
from .client import SMPPClient

__all__ = ['connect', 'Client', 'Address', 'SendResult', 'Message', 'DeliveryReceipt']

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Address:
    """An SMPP address with its type of number and numbering plan."""

    addr: str
    ton: int = TonType.UNKNOWN
    npi: int = NpiType.UNKNOWN

    @classmethod
    def parse(cls, s: Union[str, 'Address']) -> 'Address':
        """
        Parse an address string.

        Spaces and '-' are ignored in numbers. '+<digits>' is international
        ISDN, plain digits are unknown/unknown, anything else (including
        non-ASCII digits) is an alphanumeric sender, kept as given.
        """
        if isinstance(s, Address):
            return s
        n = s.replace(' ', '').replace('-', '')
        if n.startswith('+') and _ascii_digits(n[1:]):
            return cls(n[1:], TonType.INTERNATIONAL, NpiType.ISDN)
        if n == '' or _ascii_digits(n):
            return cls(n, TonType.UNKNOWN, NpiType.UNKNOWN)
        return cls(s, TonType.ALPHANUMERIC, NpiType.UNKNOWN)


def _ascii_digits(s: str) -> bool:
    return s.isascii() and s.isdigit()


@dataclass(frozen=True)
class SendResult:
    """Outcome of Client.send: one SMSC message_id per part."""

    message_ids: Tuple[str, ...]
    parts: int
    data_coding: DataCoding


@dataclass(frozen=True)
class DeliveryReceipt:
    """A parsed delivery receipt; TLVs take precedence over the receipt text."""

    id: Optional[str] = None
    state: Optional[MessageState] = None
    stat: Optional[str] = None
    err: Optional[str] = None
    submit_date: Optional[str] = None
    done_date: Optional[str] = None
    text: Optional[str] = None


@dataclass(frozen=True)
class Message:
    """An inbound message, decoded and reassembled."""

    sender: Address
    to: Address
    text: Optional[str]
    receipt: Optional[DeliveryReceipt]
    pdu: Union[DeliverSm, DataSm]

    @property
    def is_receipt(self) -> bool:
        return self.receipt is not None


_STAT_TO_STATE = {
    'DELIVRD': MessageState.DELIVERED,
    'EXPIRED': MessageState.EXPIRED,
    'DELETED': MessageState.DELETED,
    'UNDELIV': MessageState.UNDELIVERABLE,
    'ACCEPTD': MessageState.ACCEPTED,
    'UNKNOWN': MessageState.UNKNOWN,
    'REJECTD': MessageState.REJECTED,
    'ENROUTE': MessageState.ENROUTE,
}


def _is_receipt(pdu: Union[DeliverSm, DataSm]) -> bool:
    # SMSC delivery receipt message type (SMPP v3.4 §5.2.12)
    return (pdu.esm_class & 0x3C) == 0x04


def _tlv(pdu: Union[DeliverSm, DataSm], tag: int) -> Union[int, str, bytes, None]:
    """get_tlv, treating a malformed TLV as absent."""
    try:
        return pdu.get_tlv(tag)
    except SMPPValidationException:
        return None


def _parse_receipt(pdu: Union[DeliverSm, DataSm]) -> DeliveryReceipt:
    """Parse a receipt from its Appendix B text, overridden by receipt TLVs."""
    # data_sm has no Appendix B text; its receipt is TLVs only
    fields = pdu.parse_delivery_receipt() if isinstance(pdu, DeliverSm) else {}
    stat = fields.get('stat')
    state = _STAT_TO_STATE.get(stat.upper()) if stat else None
    receipt_id = fields.get('id')

    tlv_id = _tlv(pdu, OptionalTag.RECEIPTED_MESSAGE_ID)
    if isinstance(tlv_id, str):
        receipt_id = tlv_id
    tlv_state = _tlv(pdu, OptionalTag.MESSAGE_STATE)
    if isinstance(tlv_state, int):
        try:
            state = MessageState(tlv_state)
        except ValueError:
            pass

    return DeliveryReceipt(
        id=receipt_id,
        state=state,
        stat=stat,
        err=fields.get('err'),
        submit_date=fields.get('submit_date'),
        done_date=fields.get('done_date'),
        text=fields.get('text'),
    )


def _decode(content: bytes, data_coding: int) -> Optional[str]:
    try:
        return decode_message_with_encoding(content, data_coding)
    except SMPPPDUException:
        return None


def _split(
    pdu: Union[DeliverSm, DataSm],
) -> Tuple[Optional[ConcatenatedSMSHeader], bytes]:
    """Concat info (from UDH, else SAR TLVs) and the message bytes without UDH."""
    if isinstance(pdu, DeliverSm) and pdu.short_message:
        raw = pdu.short_message
    else:
        raw = pdu.get_optional_parameter_value(OptionalTag.MESSAGE_PAYLOAD) or b''
    if pdu.esm_class & 0x40:  # UDHI
        try:
            udh, offset = UDH.decode(raw)
            raw = raw[offset:]
            element = udh.get_element(UDH.IEI_CONCATENATED_SMS_8BIT) or udh.get_element(
                UDH.IEI_CONCATENATED_SMS_16BIT
            )
            if element:
                return ConcatenatedSMSHeader.from_udh_element(element), raw
        except ValueError:
            pass  # malformed UDH: keep the bytes as they are
    ref = _tlv(pdu, OptionalTag.SAR_MSG_REF_NUM)
    total = _tlv(pdu, OptionalTag.SAR_TOTAL_SEGMENTS)
    seq = _tlv(pdu, OptionalTag.SAR_SEGMENT_SEQNUM)
    if isinstance(ref, int) and isinstance(total, int) and isinstance(seq, int):
        return ConcatenatedSMSHeader(
            reference=ref, total_parts=total, part_number=seq
        ), raw
    return None, raw


def _to_message(pdu: Union[DeliverSm, DataSm], text: Optional[str]) -> Message:
    return Message(
        sender=Address(pdu.source_addr, pdu.source_addr_ton, pdu.source_addr_npi),
        to=Address(pdu.destination_addr, pdu.dest_addr_ton, pdu.dest_addr_npi),
        text=text,
        receipt=_parse_receipt(pdu) if _is_receipt(pdu) else None,
        pdu=pdu,
    )


_CLOSED = object()
_PartKey = Tuple[str, str, int, int]
# ponytail: fixed cap, expose it on connect() if someone needs to tune it
_MAX_PENDING = 1000
_PART_TTL = 300.0  # seconds an incomplete part set may wait


class Client:
    """High-level client; built by smpp.connect(), wraps an SMPPClient."""

    def __init__(self, raw: SMPPClient):
        self.raw = raw
        # Unbounded so terminal items always fit; _put caps the Messages.
        self._queue: asyncio.Queue = asyncio.Queue()
        # key -> (first-arrival monotonic time, part_number -> pdu)
        self._parts: Dict[
            _PartKey, Tuple[float, Dict[int, Union[DeliverSm, DataSm]]]
        ] = {}
        self._consuming = False
        self._closing = False
        raw.on_deliver_sm = self._on_message
        raw.on_data_sm = self._on_message
        raw.on_connection_lost = self._on_connection_lost

    async def send(
        self,
        to: Union[str, Address],
        text: str,
        *,
        sender: Union[str, Address] = '',
        receipt: bool = False,
        timeout: Optional[float] = None,
    ) -> SendResult:
        """
        Send text, as GSM-7 if it fits the alphabet else UCS2, split into
        concatenated parts as needed.

        Raises:
            SMPPMessageException / SMPPThrottlingException from submit_multipart;
            a mid-sequence failure carries `.sent_message_ids`.
        """
        dest = Address.parse(to)
        src = Address.parse(sender)
        try:
            encode_message_with_encoding(text, DataCoding.DEFAULT)
            data_coding = DataCoding.DEFAULT
        except SMPPPDUException:
            data_coding = DataCoding.UCS2
        ids = await self.raw.submit_multipart(
            src.addr,
            dest.addr,
            text,
            data_coding=data_coding,
            registered_delivery=RegisteredDelivery.SUCCESS_FAILURE
            if receipt
            else RegisteredDelivery.NO_RECEIPT,
            timeout=timeout,
            source_addr_ton=src.ton,
            source_addr_npi=src.npi,
            dest_addr_ton=dest.ton,
            dest_addr_npi=dest.npi,
        )
        return SendResult(tuple(ids), len(ids), data_coding)

    async def messages(self) -> AsyncIterator[Message]:
        """
        Yield inbound messages until the connect() block exits.

        Only one consumer at a time; raises the loss exception if the
        connection drops.
        """
        if self._consuming:
            raise RuntimeError('messages() already has a consumer')
        self._consuming = True
        try:
            while True:
                item = await self._queue.get()
                if isinstance(item, Message):
                    yield item
                    continue
                self._queue.put_nowait(item)  # keep it terminal for later calls
                if isinstance(item, Exception):
                    raise item
                return
        finally:
            self._consuming = False

    def _on_message(self, raw: SMPPClient, pdu: Union[DeliverSm, DataSm]) -> None:
        info, content = _split(pdu)
        if (
            info is None
            or _is_receipt(pdu)
            or not 1 <= info.part_number <= info.total_parts
        ):
            self._put(_to_message(pdu, _decode(content, pdu.data_coding)))
            return

        now = time.monotonic()
        for k in [k for k, (t, _) in self._parts.items() if now - t > _PART_TTL]:
            logger.warning('Discarding incomplete concatenated message %s', k)
            del self._parts[k]
        # ponytail: two sets sharing the 8-bit reference within the TTL still
        # collide; inherent to the reference size, 16-bit refs make it rarer
        key = (pdu.source_addr, pdu.destination_addr, info.reference, info.total_parts)
        received = self._parts.setdefault(key, (now, {}))[1]
        received[info.part_number] = pdu
        if len(received) < info.total_parts:
            return
        del self._parts[key]
        parts = [
            MessagePart(
                content=_split(p)[1],
                part_number=n,
                total_parts=info.total_parts,
                reference=info.reference,
            )
            for n, p in received.items()
        ]
        try:
            text: Optional[str] = reassemble_parts(parts, pdu.data_coding)
        except (ValueError, SMPPPDUException):
            text = None
        self._put(_to_message(pdu, text))

    def _put(self, msg: Message) -> None:
        # Only Messages are queued before a terminal item, so the oldest
        # item is always a Message while the cap is reached.
        if self._queue.qsize() >= _MAX_PENDING:
            self._queue.get_nowait()
            logger.warning('Dropped oldest inbound message: %d unread', _MAX_PENDING)
        self._queue.put_nowait(msg)

    def _on_connection_lost(self, raw: SMPPClient, error: Exception) -> None:
        if not self._closing:
            self._queue.put_nowait(error)

    def _close(self) -> None:
        self._queue.put_nowait(_CLOSED)


_BIND_METHODS = {
    'tx': 'bind_transmitter',
    'rx': 'bind_receiver',
    'trx': 'bind_transceiver',
}


@asynccontextmanager
async def connect(
    host: str,
    port: int,
    system_id: str,
    password: str,
    *,
    bind: Literal['tx', 'rx', 'trx'] = 'trx',
    **client_kwargs,
) -> AsyncIterator[Client]:
    """
    Connect and bind to an SMSC; unbind and disconnect on exit.

    Args:
        bind: 'tx' (transmitter), 'rx' (receiver) or 'trx' (transceiver)
        **client_kwargs: Extra SMPPClient constructor arguments
    """
    if bind not in _BIND_METHODS:
        raise ValueError(f"bind must be 'tx', 'rx' or 'trx', not {bind!r}")
    raw = SMPPClient(host, port, system_id, password, **client_kwargs)
    client = Client(raw)
    await raw.connect()
    try:
        await getattr(raw, _BIND_METHODS[bind])()
        yield client
    finally:
        client._closing = True
        try:
            await raw.disconnect()
        finally:
            client._close()
