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
import typing as tp

from ..exceptions import SMPPPDUException
from ..gsm import MessagePart, reassemble_parts
from ..message import (
    Address,
    DeliveryReceipt,
    Message,
    _decode,
    _is_receipt,
    _split,
    _to_message,
)
from ..protocol import DataCoding, DataSm, DeliverSm, RegisteredDelivery
from ..protocol.codec import encode_message_with_encoding
from .client import SMPPClient

__all__ = ['connect', 'Client', 'Address', 'SendResult', 'Message', 'DeliveryReceipt']

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SendResult:
    """Outcome of Client.send: one SMSC message_id per part."""

    message_ids: tp.Tuple[str, ...]
    parts: int
    data_coding: DataCoding


_CLOSED = object()
_PartKey = tp.Tuple[str, str, int, int]
# ponytail: fixed cap, expose it on connect() if someone needs to tune it
_MAX_PENDING = 1000
# ponytail: fixed cap, expose it on connect() if someone needs to tune it
_MAX_PART_SETS = 1000
_PART_TTL = 300.0  # seconds an incomplete part set may wait


class Client:
    """High-level client; built by smpp.connect(), wraps an SMPPClient."""

    def __init__(self, raw: SMPPClient):
        self.raw = raw
        # Unbounded so terminal items always fit; _put caps the Messages.
        self._queue: asyncio.Queue = asyncio.Queue()
        # key -> (first-arrival monotonic time, part_number -> pdu)
        self._parts: tp.Dict[
            _PartKey, tp.Tuple[float, tp.Dict[int, tp.Union[DeliverSm, DataSm]]]
        ] = {}
        self._consuming = False
        self._closing = False
        self._ended = False  # a terminal item is queued
        self._dropped = 0  # messages dropped in the current overflow episode
        self._evicted = 0  # part sets evicted in the current cap episode
        raw.on_deliver_sm = self._on_message
        raw.on_data_sm = self._on_message
        raw.on_connection_lost = self._on_connection_lost

    async def send(
        self,
        to: tp.Union[str, Address],
        text: str,
        *,
        sender: tp.Union[str, Address] = '',
        receipt: bool = False,
        timeout: tp.Optional[float] = None,
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

    async def messages(self) -> tp.AsyncIterator[Message]:
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

    def _on_message(self, raw: SMPPClient, pdu: tp.Union[DeliverSm, DataSm]) -> None:
        info, content = _split(pdu)
        if (
            info is None
            or _is_receipt(pdu)
            or not 1 <= info.part_number <= info.total_parts
        ):
            self._put(_to_message(pdu, _decode(content, pdu.data_coding)))
            return

        now = time.monotonic()
        # ponytail: two sets sharing the 8-bit reference within the TTL still
        # collide; inherent to the reference size, 16-bit refs make it rarer
        key = (pdu.source_addr, pdu.destination_addr, info.reference, info.total_parts)
        # Insertion order + setdefault keeps the head the oldest set, so stop
        # at the first one that is neither expired nor over the cap.
        expired = evicted = 0
        while self._parts:
            head, (t, _) = next(iter(self._parts.items()))
            if now - t > _PART_TTL:
                expired += 1
            elif len(self._parts) >= _MAX_PART_SETS and key not in self._parts:
                evicted += 1
            else:
                break
            del self._parts[head]
        if expired:
            logger.warning(
                'Discarded %d incomplete concatenated message(s) after %.0f s',
                expired,
                _PART_TTL,
            )
        if evicted:
            if not self._evicted:
                logger.warning(
                    'Too many incomplete concatenated messages (%d): discarding oldest',
                    _MAX_PART_SETS,
                )
            self._evicted += evicted
        elif self._evicted and key not in self._parts:
            logger.warning(
                'Incomplete concatenated messages back under the cap: discarded %d',
                self._evicted,
            )
            self._evicted = 0
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
            text: tp.Optional[str] = reassemble_parts(parts, pdu.data_coding)
        except (ValueError, SMPPPDUException):
            text = None
        self._put(_to_message(pdu, text))

    def _put(self, msg: Message) -> None:
        # Until a terminal item is queued every item is a Message, so the
        # oldest can be evicted. After it, never evict: the terminal item must
        # survive, and stragglers (already acked) stay bounded as the link is dead.
        if self._ended:
            self._queue.put_nowait(msg)
            return
        if self._queue.qsize() >= _MAX_PENDING:
            self._queue.get_nowait()
            if not self._dropped:
                logger.warning(
                    'Inbound queue full (%d unread): dropping oldest messages',
                    _MAX_PENDING,
                )
            self._dropped += 1
        elif self._dropped:
            logger.warning(
                'Inbound queue has room again: dropped %d messages', self._dropped
            )
            self._dropped = 0
        self._queue.put_nowait(msg)

    def _on_connection_lost(self, raw: SMPPClient, error: Exception) -> None:
        if not self._closing:
            self._ended = True
            self._queue.put_nowait(error)

    def _close(self) -> None:
        self._ended = True
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
    bind: tp.Literal['tx', 'rx', 'trx'] = 'trx',
    **client_kwargs,
) -> tp.AsyncIterator[Client]:
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
