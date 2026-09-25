"""
Tests for the high-level client API (smpp.connect / Client).
"""

import asyncio
from types import SimpleNamespace

import pytest
import pytest_asyncio

import smpp
from smpp import (
    Address,
    DataCoding,
    DataSm,
    DeliverSm,
    MessageState,
    NpiType,
    OptionalTag,
    TonType,
)
from smpp.client.highlevel import _parse_receipt, _to_message
from smpp.gsm import make_parts
from smpp.server import SMPPServer

RECEIPT_TEXT = (
    'id:abc123 sub:001 dlvrd:001 submit date:2609241200 '
    'done date:2609241201 stat:DELIVRD err:000 text:Hello'
)


def _receipt_pdu(text: str) -> DeliverSm:
    pdu = DeliverSm(source_addr='306900000000', destination_addr='ACME', esm_class=0x04)  # type: ignore[call-arg]
    pdu.set_message_text(text)
    return pdu


class TestAddressParse:
    def test_international(self):
        assert Address.parse('+306900000000') == Address(
            '306900000000', TonType.INTERNATIONAL, NpiType.ISDN
        )

    def test_digits(self):
        assert Address.parse('6900000000') == Address(
            '6900000000', TonType.UNKNOWN, NpiType.UNKNOWN
        )

    def test_alphanumeric(self):
        assert Address.parse('ACME') == Address(
            'ACME', TonType.ALPHANUMERIC, NpiType.UNKNOWN
        )

    def test_empty(self):
        assert Address.parse('') == Address('', TonType.UNKNOWN, NpiType.UNKNOWN)

    @pytest.mark.parametrize('s', ['+30 690 000 0000', '+30-690-000-0000'])
    def test_formatted_international(self, s):
        assert Address.parse(s) == Address(
            '306900000000', TonType.INTERNATIONAL, NpiType.ISDN
        )

    def test_formatted_digits(self):
        assert Address.parse('690 000') == Address(
            '690000', TonType.UNKNOWN, NpiType.UNKNOWN
        )

    def test_alphanumeric_keeps_hyphen(self):
        assert Address.parse('ACME-Co') == Address(
            'ACME-Co', TonType.ALPHANUMERIC, NpiType.UNKNOWN
        )

    def test_non_ascii_digits_are_alphanumeric(self):
        assert Address.parse('+٣٠٦').ton == TonType.ALPHANUMERIC


class TestParseReceipt:
    def test_appendix_b_text(self):
        r = _parse_receipt(_receipt_pdu(RECEIPT_TEXT))
        assert r.id == 'abc123'
        assert r.state == MessageState.DELIVERED
        assert r.stat == 'DELIVRD'
        assert r.err == '000'
        assert r.text == 'Hello'

    def test_tlvs_override_text(self):
        pdu = _receipt_pdu(RECEIPT_TEXT)
        pdu.set_tlv(OptionalTag.RECEIPTED_MESSAGE_ID, 'tlv-id')
        pdu.set_tlv(OptionalTag.MESSAGE_STATE, 5)
        r = _parse_receipt(pdu)
        assert r.id == 'tlv-id'
        assert r.state == MessageState.UNDELIVERABLE

    def test_malformed_tlv_falls_back_to_text(self):
        pdu = _receipt_pdu(RECEIPT_TEXT)
        pdu.add_optional_parameter(OptionalTag.MESSAGE_STATE, b'\x00\x02')
        assert _parse_receipt(pdu).state == MessageState.DELIVERED

    def test_out_of_range_state_falls_back_to_text(self):
        pdu = _receipt_pdu(RECEIPT_TEXT)
        pdu.set_tlv(OptionalTag.MESSAGE_STATE, 0)
        assert _parse_receipt(pdu).state == MessageState.DELIVERED

    def test_garbage_text(self):
        msg = _to_message(_receipt_pdu('not a receipt'), 'not a receipt')
        assert msg.text == 'not a receipt'
        assert msg.receipt == smpp.DeliveryReceipt()


class TestConnectArgs:
    @pytest.mark.asyncio
    async def test_bad_bind_raises_before_connecting(self):
        # Port 1 is never listening; ValueError must come first.
        with pytest.raises(ValueError):
            async with smpp.connect('127.0.0.1', 1, 'u', 'p', bind='xx'):  # type: ignore[arg-type]
                pass


@pytest_asyncio.fixture
async def server():
    srv = SMPPServer(host='127.0.0.1', port=0, setup_signal_handlers=False)
    srv.configure_shutdown(grace_period=0.1, reminder_delay=0.1, shutdown_timeout=0.5)
    srv.received = []
    srv.on_message_received = lambda s, session, pdu: srv.received.append(pdu)
    await srv.start()
    srv.test_port = srv._server.sockets[0].getsockname()[1]
    yield srv
    await srv.stop()


def _session(server):
    return next(s for s in server._clients.values() if s.bound)


@pytest.mark.asyncio
class TestLoopback:
    async def test_send_long_gsm_with_receipt(self, server):
        async with smpp.connect('127.0.0.1', server.test_port, 'u', 'p') as c:
            result = await c.send(
                '+306900000000', 'x' * 200, sender='ACME', receipt=True
            )
            assert result.parts == 2
            assert len(result.message_ids) == 2
            assert result.data_coding == DataCoding.DEFAULT
            pdu = server.received[0]
            assert pdu.data_coding == 0
            assert pdu.registered_delivery == 1
            assert pdu.dest_addr_ton == TonType.INTERNATIONAL
            assert pdu.source_addr_ton == TonType.ALPHANUMERIC

    async def test_send_non_gsm_uses_ucs2(self, server):
        async with smpp.connect('127.0.0.1', server.test_port, 'u', 'p') as c:
            result = await c.send('6900000000', 'Γειά 👋')
            assert result.data_coding == DataCoding.UCS2
            assert server.received[0].data_coding == DataCoding.UCS2

    async def test_messages_decodes_receipts_and_reassembles(self, server):
        async with smpp.connect('127.0.0.1', server.test_port, 'u', 'p') as c:
            got = []

            async def consume():
                async for m in c.messages():
                    got.append(m)

            consumer = asyncio.create_task(consume())
            await asyncio.sleep(0)
            with pytest.raises(RuntimeError):
                async for _ in c.messages():
                    pass

            assert await server.deliver_sm('u', '306900000000', 'ACME', 'hi there')
            assert await server.deliver_sm(
                'u', '306900000000', 'ACME', RECEIPT_TEXT, esm_class=0x04
            )
            session = _session(server)
            for part in make_parts('y' * 200, DataCoding.DEFAULT):
                pdu = DeliverSm(  # type: ignore[call-arg]
                    source_addr='306900000000',
                    destination_addr='ACME',
                    esm_class=0x40,
                    data_coding=DataCoding.DEFAULT,
                    short_message=part.get_short_message(),
                )
                await session.connection.send_pdu(pdu, wait_response=True)
            while len(got) < 3:
                await asyncio.sleep(0.01)
        # Leaving the connect() block ends iteration.
        await asyncio.wait_for(consumer, 1)

        plain, receipt, long = got
        assert plain.text == 'hi there'
        assert plain.is_receipt is False
        assert plain.sender == Address('306900000000')
        assert receipt.is_receipt
        assert receipt.receipt.id == 'abc123'
        assert long.text == 'y' * 200
        assert long.is_receipt is False


@pytest.mark.asyncio
async def test_messages_raises_on_connection_lost():
    from smpp.client.highlevel import Client

    c = Client(smpp.SMPPClient('127.0.0.1', 1, 'u', 'p'))
    lost = ConnectionError('gone')
    c.raw.on_connection_lost(c.raw, lost)
    with pytest.raises(ConnectionError):
        async for _ in c.messages():
            pass


def _client():
    from smpp.client.highlevel import Client

    return Client(smpp.SMPPClient('127.0.0.1', 1, 'u', 'p'))


def _part_pdus(text: str, reference: int):
    return [
        DeliverSm(  # type: ignore[call-arg]
            source_addr='306900000000',
            destination_addr='ACME',
            esm_class=0x40,
            data_coding=DataCoding.DEFAULT,
            short_message=part.get_short_message(),
        )
        for part in make_parts(text, DataCoding.DEFAULT, reference=reference)
    ]


async def _drain(c):
    c._close()
    return [m async for m in c.messages()]


@pytest.mark.asyncio
async def test_queue_drops_oldest_beyond_cap(monkeypatch):
    from smpp.client import highlevel

    monkeypatch.setattr(highlevel, '_MAX_PENDING', 3)
    c = _client()
    for i in range(5):
        pdu = DeliverSm(source_addr='1', destination_addr='2')  # type: ignore[call-arg]
        pdu.set_message_text(f'm{i}')
        c._on_message(c.raw, pdu)
    assert [m.text for m in await _drain(c)] == ['m2', 'm3', 'm4']


@pytest.mark.asyncio
async def test_stale_part_set_is_evicted(monkeypatch):
    from smpp.client import highlevel

    c = _client()
    a1, _ = _part_pdus('a' * 200, reference=5)
    b1, b2 = _part_pdus('b' * 200, reference=5)
    c._on_message(c.raw, a1)
    monkeypatch.setattr(highlevel, '_PART_TTL', -1)
    c._on_message(c.raw, b2)  # without eviction, a1 + b2 would complete
    monkeypatch.setattr(highlevel, '_PART_TTL', 300.0)
    c._on_message(c.raw, b1)
    assert [m.text for m in await _drain(c)] == ['b' * 200]


def _text_pdu(text: str) -> DeliverSm:
    pdu = DeliverSm(source_addr='306900000000', destination_addr='ACME')  # type: ignore[call-arg]
    pdu.set_message_text(text)
    return pdu


@pytest.mark.asyncio
async def test_queue_never_evicts_terminal(monkeypatch):
    from smpp.client import highlevel

    monkeypatch.setattr(highlevel, '_MAX_PENDING', 2)
    c = _client()
    c._on_message(c.raw, _text_pdu('m0'))
    c.raw.on_connection_lost(c.raw, ConnectionError())
    for i in range(1, 4):
        c._on_message(c.raw, _text_pdu(f'm{i}'))
    for expected in (['m0'], ['m1', 'm2', 'm3']):
        got = []

        async def consume():
            async for m in c.messages():
                got.append(m.text)

        with pytest.raises(ConnectionError):
            await asyncio.wait_for(consume(), 1)  # an evicted error would hang
        assert got == expected


@pytest.mark.asyncio
async def test_part_set_cap_evicts_oldest(monkeypatch):
    from smpp.client import highlevel

    monkeypatch.setattr(highlevel, '_MAX_PART_SETS', 2)
    c = _client()
    sets = {ref: _part_pdus(f'{ref}' * 200, reference=ref) for ref in (1, 2, 3)}
    for ref in (1, 2, 3):
        c._on_message(c.raw, sets[ref][0])
    assert not any(k[2] == 1 for k in c._parts)
    c._on_message(c.raw, sets[3][1])
    assert [m.text for m in await _drain(c)] == ['3' * 200]


@pytest.mark.asyncio
async def test_part_set_cap_spares_own_key(monkeypatch):
    from smpp.client import highlevel

    monkeypatch.setattr(highlevel, '_MAX_PART_SETS', 1)
    c = _client()
    for p in _part_pdus('a' * 200, reference=1):
        c._on_message(c.raw, p)
    assert [m.text for m in await _drain(c)] == ['a' * 200]


def _clock(monkeypatch, highlevel):
    # Patch the module's view of time only; asyncio reads time.monotonic too.
    now = [0.0]
    monkeypatch.setattr(highlevel, 'time', SimpleNamespace(monotonic=lambda: now[0]))
    return now


@pytest.mark.asyncio
async def test_sweep_keeps_young_sets(monkeypatch):
    from smpp.client import highlevel

    now = _clock(monkeypatch, highlevel)
    c = _client()
    a1, _ = _part_pdus('a' * 200, reference=1)
    b1, b2 = _part_pdus('b' * 200, reference=2)
    c._on_message(c.raw, a1)
    now[0] = 200.0
    c._on_message(c.raw, b1)
    now[0] = 350.0
    c._on_message(c.raw, b2)
    assert c._parts == {}
    assert [m.text for m in await _drain(c)] == ['b' * 200]


@pytest.mark.asyncio
async def test_overflow_logs_once_per_episode(monkeypatch, caplog):
    from smpp.client import highlevel

    monkeypatch.setattr(highlevel, '_MAX_PENDING', 3)
    c = _client()
    for i in range(6):
        c._on_message(c.raw, _text_pdu(f'm{i}'))
    assert caplog.text.count('dropping oldest') == 1
    for _ in range(3):
        c._queue.get_nowait()
    c._on_message(c.raw, _text_pdu('m6'))
    (room,) = [r for r in caplog.records if 'room again' in r.message]
    assert room.levelname == 'WARNING' and '3' in room.message


@pytest.mark.asyncio
async def test_part_logs_carry_no_msisdn(monkeypatch, caplog):
    from smpp.client import highlevel

    now = _clock(monkeypatch, highlevel)
    monkeypatch.setattr(highlevel, '_MAX_PART_SETS', 1)
    c = _client()
    c._on_message(c.raw, _part_pdus('a' * 200, reference=1)[0])
    now[0] = 400.0
    c._on_message(c.raw, _part_pdus('b' * 200, reference=2)[0])  # a expires
    c._on_message(c.raw, _part_pdus('c' * 200, reference=3)[0])  # b evicted
    warnings = [r for r in caplog.records if r.levelname == 'WARNING']
    assert len(warnings) == 2
    assert 'after' in warnings[0].message and 'discarding oldest' in warnings[1].message
    assert '306900000000' not in caplog.text


@pytest.mark.asyncio
async def test_out_of_range_part_number_is_standalone():
    c = _client()
    _, p2 = _part_pdus('z' * 200, reference=7)
    udh = bytearray(p2.short_message)
    assert udh[:3] == b'\x05\x00\x03'
    udh[5] = 3  # part 3 of 2
    p2.short_message = bytes(udh)
    c._on_message(c.raw, p2)
    assert c._parts == {}
    (msg,) = await _drain(c)
    assert msg.pdu is p2


@pytest.mark.asyncio
async def test_connection_lost_while_closing_ends_cleanly():
    c = _client()
    c._closing = True
    c.raw.on_connection_lost(c.raw, ConnectionError())
    assert await _drain(c) == []


@pytest.mark.asyncio
async def test_messages_ends_when_disconnect_fails(server):
    with pytest.raises(RuntimeError):
        async with smpp.connect('127.0.0.1', server.test_port, 'u', 'p') as c:
            consumer = asyncio.create_task(_consume(c))
            await asyncio.sleep(0)
            real_disconnect = c.raw.disconnect

            async def boom():
                raise RuntimeError('unbind failed')

            c.raw.disconnect = boom  # type: ignore[method-assign]
    await asyncio.wait_for(consumer, 1)
    await real_disconnect()


async def _consume(c):
    async for _ in c.messages():
        pass


def test_client_sets_data_sm_handler():
    c = _client()
    assert c.raw.on_deliver_sm == c._on_message
    assert c.raw.on_data_sm == c._on_message


@pytest.mark.asyncio
async def test_data_sm_yields_message():
    c = _client()
    pdu = DataSm(source_addr='1', destination_addr='2')  # type: ignore[call-arg]
    pdu.set_message_text('hello')
    c._on_message(c.raw, pdu)
    (msg,) = await _drain(c)
    assert msg.text == 'hello'
    assert msg.receipt is None
    assert msg.pdu is pdu


@pytest.mark.asyncio
async def test_data_sm_receipt_from_tlvs():
    c = _client()
    pdu = DataSm(source_addr='1', destination_addr='2', esm_class=0x04)  # type: ignore[call-arg]
    pdu.set_tlv(OptionalTag.RECEIPTED_MESSAGE_ID, 'tlv-id')
    pdu.set_tlv(OptionalTag.MESSAGE_STATE, MessageState.DELIVERED)
    c._on_message(c.raw, pdu)
    (msg,) = await _drain(c)
    assert msg.is_receipt
    assert msg.receipt.id == 'tlv-id'
    assert msg.receipt.state == MessageState.DELIVERED


def _sar(pdu, ref, total, seq):
    pdu.set_tlv(OptionalTag.SAR_MSG_REF_NUM, ref)
    pdu.set_tlv(OptionalTag.SAR_TOTAL_SEGMENTS, total)
    pdu.set_tlv(OptionalTag.SAR_SEGMENT_SEQNUM, seq)
    return pdu


@pytest.mark.asyncio
async def test_data_sm_udh_parts_reassembled():
    c = _client()
    text = 'Ω' * 80
    for part in make_parts(text, DataCoding.UCS2, reference=7):
        pdu = DataSm(  # type: ignore[call-arg]
            source_addr='1',
            destination_addr='2',
            esm_class=0x40,
            data_coding=DataCoding.UCS2,
        )
        pdu.set_message_payload(part.get_short_message())
        c._on_message(c.raw, pdu)
    (msg,) = await _drain(c)
    assert msg.text == text


@pytest.mark.asyncio
async def test_data_sm_sar_parts_reassembled():
    c = _client()
    halves = []
    for n, chunk in enumerate([b'hello ', b'world'], 1):
        pdu = DataSm(source_addr='1', destination_addr='2')  # type: ignore[call-arg]
        pdu.set_message_payload(chunk)
        halves.append(_sar(pdu, 300, 2, n))
    c._on_message(c.raw, halves[1])
    c._on_message(c.raw, halves[0])
    (msg,) = await _drain(c)
    assert msg.text == 'hello world'


@pytest.mark.asyncio
async def test_deliver_sm_payload_udh_parts_reassembled():
    c = _client()
    text = 'Ω' * 80
    for part in make_parts(text, DataCoding.UCS2, reference=7):
        pdu = DeliverSm(  # type: ignore[call-arg]
            source_addr='1',
            destination_addr='2',
            esm_class=0x40,
            data_coding=DataCoding.UCS2,
        )
        pdu.set_tlv(OptionalTag.MESSAGE_PAYLOAD, part.get_short_message())
        c._on_message(c.raw, pdu)
    (msg,) = await _drain(c)
    assert msg.text == text


@pytest.mark.asyncio
async def test_deliver_sm_sar_parts_reassembled():
    c = _client()
    for n, chunk in enumerate([b'hello ', b'world'], 1):
        pdu = DeliverSm(source_addr='1', destination_addr='2', short_message=chunk)  # type: ignore[call-arg]
        c._on_message(c.raw, _sar(pdu, 9, 2, n))
    (msg,) = await _drain(c)
    assert msg.text == 'hello world'


@pytest.mark.asyncio
async def test_single_data_sm_with_udh_strips_header():
    c = _client()
    pdu = DataSm(source_addr='1', destination_addr='2', esm_class=0x40)  # type: ignore[call-arg]
    pdu.set_message_payload(b'\x00hello')
    c._on_message(c.raw, pdu)
    (msg,) = await _drain(c)
    assert msg.text == 'hello'


@pytest.mark.asyncio
async def test_malformed_udh_is_standalone():
    c = _client()
    pdu = DataSm(source_addr='1', destination_addr='2', esm_class=0x40)  # type: ignore[call-arg]
    pdu.set_message_payload(b'\x09ab')
    c._on_message(c.raw, pdu)
    assert c._parts == {}
    (msg,) = await _drain(c)
    assert msg.pdu is pdu
