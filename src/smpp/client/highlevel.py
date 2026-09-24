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
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import AsyncIterator, Dict, Literal, Optional, Tuple, Union

from ..exceptions import SMPPPDUException, SMPPValidationException
from ..gsm import MessagePart, reassemble_parts
from ..protocol import (
    DataCoding,
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

        '+<digits>' is international ISDN, plain digits are unknown/unknown,
        anything else is an alphanumeric sender.
        """
        if isinstance(s, Address):
            return s
        if s.startswith('+') and s[1:].isdigit():
            return cls(s[1:], TonType.INTERNATIONAL, NpiType.ISDN)
        if s == '' or s.isdigit():
            return cls(s, TonType.UNKNOWN, NpiType.UNKNOWN)
        return cls(s, TonType.ALPHANUMERIC, NpiType.UNKNOWN)


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
    pdu: DeliverSm

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


def _is_receipt(pdu: DeliverSm) -> bool:
    # SMSC delivery receipt message type (SMPP v3.4 §5.2.12)
    return (pdu.esm_class & 0x3C) == 0x04


def _tlv(pdu: DeliverSm, tag: int) -> Union[int, str, bytes, None]:
    """get_tlv, treating a malformed TLV as absent."""
    try:
        return pdu.get_tlv(tag)
    except SMPPValidationException:
        return None


def _parse_receipt(pdu: DeliverSm) -> DeliveryReceipt:
    """Parse a receipt from its Appendix B text, overridden by receipt TLVs."""
    fields = pdu.parse_delivery_receipt()
    stat = fields.get('stat')
    state = _STAT_TO_STATE.get(stat.upper()) if stat else None
    receipt_id = fields.get('id')

    tlv_id = _tlv(pdu, OptionalTag.RECEIPTED_MESSAGE_ID)
    if isinstance(tlv_id, str):
        receipt_id = tlv_id
    tlv_state = _tlv(pdu, OptionalTag.MESSAGE_STATE)
    if isinstance(tlv_state, int) and tlv_state in MessageState._value2member_map_:
        state = MessageState(tlv_state)

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


def _content(pdu: DeliverSm) -> bytes:
    """Message bytes without UDH, from short_message or message_payload."""
    if pdu.short_message:
        return pdu.get_message_content()
    return pdu.get_optional_parameter_value(OptionalTag.MESSAGE_PAYLOAD) or b''


def _to_message(pdu: DeliverSm, text: Optional[str]) -> Message:
    return Message(
        sender=Address(pdu.source_addr, pdu.source_addr_ton, pdu.source_addr_npi),
        to=Address(pdu.destination_addr, pdu.dest_addr_ton, pdu.dest_addr_npi),
        text=text,
        receipt=_parse_receipt(pdu) if _is_receipt(pdu) else None,
        pdu=pdu,
    )


_CLOSED = object()
_PartKey = Tuple[str, str, int, int]


class Client:
    """High-level client; built by smpp.connect(), wraps an SMPPClient."""

    def __init__(self, raw: SMPPClient):
        self.raw = raw
        # ponytail: unbounded queue, add maxsize/backpressure if a consumer can stall
        self._queue: asyncio.Queue = asyncio.Queue()
        # ponytail: no eviction of incomplete part sets, add a TTL if SMSCs drop parts
        self._parts: Dict[_PartKey, Dict[int, DeliverSm]] = {}
        self._consuming = False
        raw.on_deliver_sm = self._on_deliver_sm
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

    def _on_deliver_sm(self, raw: SMPPClient, pdu: DeliverSm) -> None:
        try:
            info = pdu.get_concatenated_info()
        except (ValueError, SMPPPDUException):
            info = None
        if info is None or _is_receipt(pdu):
            self._queue.put_nowait(
                _to_message(pdu, _decode(_content(pdu), pdu.data_coding))
            )
            return

        key = (pdu.source_addr, pdu.destination_addr, info.reference, info.total_parts)
        received = self._parts.setdefault(key, {})
        received[info.part_number] = pdu
        if len(received) < info.total_parts:
            return
        del self._parts[key]
        parts = [
            MessagePart(
                content=_content(p),
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
        self._queue.put_nowait(_to_message(pdu, text))

    def _on_connection_lost(self, raw: SMPPClient, error: Exception) -> None:
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
        await raw.disconnect()
        client._close()
