"""Tests for the high-level server API (smpp.Server)."""

import asyncio

import pytest
import pytest_asyncio

import smpp
from smpp import Address


def test_shutdown_lands_on_raw():
    server = smpp.Server(shutdown=smpp.Shutdown(grace=1, reminder=2, timeout=3))
    config = server.raw.get_shutdown_config()
    assert config['grace_period'] == 1
    assert config['reminder_delay'] == 2
    assert config['shutdown_timeout'] == 3


def test_invalid_shutdown_raises_like_configure_shutdown():
    with pytest.raises(ValueError, match='grace_period must be non-negative'):
        smpp.Server(shutdown=smpp.Shutdown(grace=-1))


@pytest_asyncio.fixture
async def server():
    srv = smpp.Server(
        '127.0.0.1',
        0,
        shutdown=smpp.Shutdown(grace=0.1, reminder=0.1, timeout=0.5),
        setup_signal_handlers=False,
    )

    @srv.authenticate
    async def auth(system_id, password, system_type):
        return password == 'ok'

    srv.seen = []

    @srv.on_submit
    async def on_submit(session, msg):
        srv.seen.append(msg)
        return 'ID9'

    async with srv:
        srv.test_port = srv.raw._server.sockets[0].getsockname()[1]
        yield srv


@pytest.mark.asyncio
class TestLoopback:
    async def test_async_authenticate_rejects_wrong_password(self, server):
        with pytest.raises(smpp.SMPPBindException):
            async with smpp.connect('127.0.0.1', server.test_port, 'u', 'bad'):
                pass

    async def test_on_submit_gets_message_and_sets_id(self, server):
        async with smpp.connect('127.0.0.1', server.test_port, 'u', 'ok') as c:
            result = await c.send('306900000000', 'hi', sender='111')
        assert result.message_ids == ('ID9',)
        [msg] = server.seen
        assert msg.text == 'hi'
        assert msg.sender == Address('111')
        assert msg.receipt is None
        assert isinstance(msg.pdu, smpp.SubmitSm)

    async def test_on_submit_fires_per_part(self, server):
        text = 'x' * 200
        async with smpp.connect('127.0.0.1', server.test_port, 'u', 'ok') as c:
            result = await c.send('306900000000', text)
        assert result.parts == 2
        assert len(server.seen) == 2
        assert ''.join(m.text for m in server.seen) == text

    async def test_async_connected_completes_before_bind(self, server):
        events = []

        async def connected(srv, session):
            events.append('connected-start')
            await asyncio.sleep(0.05)
            events.append('connected-end')

        server.raw.on_client_connected = connected
        server.raw.on_client_bound = lambda srv, session: events.append('bound')
        async with smpp.connect('127.0.0.1', server.test_port, 'u', 'ok'):
            pass
        assert events == ['connected-start', 'connected-end', 'bound']

    async def test_stop_during_async_connected_closes_connection(self, server):
        started = asyncio.Event()

        async def connected(srv, session):
            started.set()
            await asyncio.sleep(0.3)

        server.raw.on_client_connected = connected
        reader, writer = await asyncio.open_connection('127.0.0.1', server.test_port)
        await started.wait()
        await asyncio.wait_for(server.stop(), 2)
        assert await asyncio.wait_for(reader.read(), 2) == b''
        writer.close()
