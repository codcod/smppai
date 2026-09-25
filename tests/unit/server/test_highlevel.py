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

    async def test_on_client_connected_can_reject_via_disconnect(self, server):
        async def connected(srv, session):
            await session.connection.disconnect()

        server.raw.on_client_connected = connected
        reader, writer = await asyncio.open_connection('127.0.0.1', server.test_port)
        assert await asyncio.wait_for(reader.read(), 1) == b''
        await asyncio.sleep(0.05)
        assert not server.raw._clients
        writer.close()

    async def test_client_gone_during_authenticate_is_not_bound(self, server):
        bound = []

        async def slow_auth(system_id, password, system_type):
            await asyncio.sleep(0.05)
            return True

        server.raw.authenticate = slow_auth
        server.raw.on_client_bound = lambda srv, session: bound.append(session)
        _, writer = await asyncio.open_connection('127.0.0.1', server.test_port)
        bind = smpp.BindTransmitter(
            sequence_number=1, system_id='u', password='ok', interface_version=0x34
        )
        writer.write(bind.encode())
        await writer.drain()
        writer.close()
        await asyncio.sleep(0.2)
        assert bound == []

    async def test_on_submit_error_is_not_acked(self, server):
        @server.on_submit
        async def on_submit(session, msg):
            raise RuntimeError('store down')

        async with smpp.connect('127.0.0.1', server.test_port, 'u', 'ok') as c:
            with pytest.raises(smpp.SMPPMessageException):
                await c.send('306900000000', 'hi')

    async def test_non_str_message_id_is_stringified(self, server):
        @server.on_submit
        async def on_submit(session, msg):
            return 42

        async with smpp.connect('127.0.0.1', server.test_port, 'u', 'ok') as c:
            result = await c.send('306900000000', 'hi')
        assert result.message_ids == ('42',)


@pytest.mark.asyncio
async def test_stop_waits_for_in_flight_on_submit():
    # 1.5 s outlasts the ~1.1 s the old shutdown kept the connection open
    srv = smpp.Server(
        '127.0.0.1',
        0,
        shutdown=smpp.Shutdown(grace=0.1, reminder=0.1, timeout=3),
        setup_signal_handlers=False,
    )
    started = asyncio.Event()

    @srv.on_submit
    async def on_submit(session, msg):
        started.set()
        await asyncio.sleep(1.5)
        return 'LATE'

    async with srv:
        port = srv.raw._server.sockets[0].getsockname()[1]
        async with smpp.connect('127.0.0.1', port, 'u', 'p') as c:
            send = asyncio.create_task(c.send('306900000000', 'hi'))
            await started.wait()
            await srv.stop()
            assert (await send).message_ids == ('LATE',)
