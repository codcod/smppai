"""
Tests for the high-level client API (smpp.connect / Client).
"""

import asyncio

import pytest
import pytest_asyncio

import smpp
from smpp import (
    Address,
    DataCoding,
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
