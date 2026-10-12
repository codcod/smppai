"""SMPP over TLS: a real loopback with the self-signed fixture in tests/fixtures/tls."""

import asyncio
import pathlib
import socket
import ssl
import struct
import threading
import time

import pytest
import pytest_asyncio

import smpp
from smpp.server import SMPPServer
from smpp.server import server as server_module
from smpp.transport import SMPPConnection

TLS_DIR = pathlib.Path(__file__).parents[2] / 'fixtures' / 'tls'
CERT = str(TLS_DIR / 'cert.pem')
KEY = str(TLS_DIR / 'key.pem')


@pytest_asyncio.fixture
async def server():
    ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ctx.load_cert_chain(CERT, KEY)
    srv = smpp.Server(
        '127.0.0.1',
        0,
        shutdown=smpp.Shutdown(grace=0.1, reminder=0.1, timeout=0.5),
        setup_signal_handlers=False,
        ssl=ctx,
    )
    srv.seen = []

    @srv.on_submit
    async def on_submit(session, msg):
        srv.seen.append(msg)
        return 'ID1'

    async with srv:
        srv.test_port = srv.raw._server.sockets[0].getsockname()[1]
        yield srv


@pytest.mark.asyncio
async def test_round_trip_over_tls(server):
    client_ctx = ssl.create_default_context(cafile=CERT)
    async with smpp.connect(
        '127.0.0.1', server.test_port, 'u', 'p', ssl=client_ctx
    ) as c:
        assert c.raw._connection._writer.get_extra_info('ssl_object') is not None

        result = await c.send('306900000000', 'over tls')
        assert result.message_ids == ('ID1',)
        assert [m.text for m in server.seen] == ['over tls']

        assert await server.raw.deliver_sm('u', '306900000000', 'ACME', 'back')
        msg = await asyncio.wait_for(anext(c.messages()), timeout=5)
        assert msg.text == 'back'


@pytest.mark.asyncio
async def test_verification_enforced(server):
    # System CAs do not trust the self-signed fixture.
    with pytest.raises(smpp.SMPPConnectionException, match='CERTIFICATE_VERIFY_FAILED'):
        async with smpp.connect('127.0.0.1', server.test_port, 'u', 'p', ssl=True):
            pass


@pytest.mark.asyncio
async def test_disconnect_bounded_when_peer_ignores_close_notify():
    ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ctx.load_cert_chain(CERT, KEY)
    listener = socket.create_server(('127.0.0.1', 0))
    release = threading.Event()

    def silent_peer():
        # Handshake, then never read again, so close_notify gets no answer.
        sock, _ = listener.accept()
        with ctx.wrap_socket(sock, server_side=True):
            release.wait(10)

    peer = threading.Thread(target=silent_peer, daemon=True)
    peer.start()
    try:
        conn = SMPPConnection(
            '127.0.0.1',
            listener.getsockname()[1],
            write_timeout=0.5,
            ssl=ssl.create_default_context(cafile=CERT),
        )
        await conn.connect()
        start = time.monotonic()
        await conn.disconnect()
        assert time.monotonic() - start < 3
        assert not conn.is_connected
    finally:
        release.set()
        peer.join(5)
        listener.close()


@pytest.mark.asyncio
async def test_server_stop_bounded_when_rejected_peer_ignores_close_notify(
    monkeypatch,
):
    monkeypatch.setattr(server_module, '_REJECT_CLOSE_TIMEOUT', 0.5)
    ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ctx.load_cert_chain(CERT, KEY)
    srv = SMPPServer(
        '127.0.0.1', 0, max_connections=0, setup_signal_handlers=False, ssl=ctx
    )
    await srv.start()
    port = srv._server.sockets[0].getsockname()[1]
    release = threading.Event()

    def silent_client():
        # Handshake, then never read again, so the server's close_notify gets no answer.
        client_ctx = ssl.create_default_context(cafile=CERT)
        sock = socket.create_connection(('127.0.0.1', port))
        with client_ctx.wrap_socket(sock, server_hostname='localhost'):
            release.wait(40)

    peer = threading.Thread(target=silent_client, daemon=True)
    peer.start()
    try:
        await asyncio.sleep(0.3)  # let the server accept and reject it
        start = time.monotonic()
        await srv.stop()
        # 3.12+ stop() waits for the rejecting handler; 3.10 leaves it running.
        handlers = [
            t for t in asyncio.all_tasks() if '_handle_client_connection' in repr(t)
        ]
        if handlers:
            await asyncio.wait(handlers, timeout=3)
        assert time.monotonic() - start < 3
        assert all(t.done() for t in handlers)
    finally:
        release.set()
        peer.join(5)


@pytest.mark.asyncio
async def test_reject_absorbs_reset_during_close(monkeypatch):
    monkeypatch.setattr(server_module, '_REJECT_CLOSE_TIMEOUT', 5)
    outcome = []
    done = asyncio.Event()
    real_close_writer = server_module.close_writer

    async def spy(writer, timeout):
        try:
            await real_close_writer(writer, timeout)
            outcome.append(None)
        except BaseException as e:
            outcome.append(e)
            raise
        finally:
            done.set()

    monkeypatch.setattr(server_module, 'close_writer', spy)
    ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ctx.load_cert_chain(CERT, KEY)
    srv = SMPPServer(
        '127.0.0.1', 0, max_connections=0, setup_signal_handlers=False, ssl=ctx
    )
    await srv.start()
    port = srv._server.sockets[0].getsockname()[1]

    def resetting_client():
        # Handshake, let the server send close_notify, then reset instead of answering.
        client_ctx = ssl.create_default_context(cafile=CERT)
        sock = socket.create_connection(('127.0.0.1', port))
        tls = client_ctx.wrap_socket(sock, server_hostname='localhost')
        time.sleep(0.3)
        tls.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack('ii', 1, 0))
        tls.close()

    peer = threading.Thread(target=resetting_client, daemon=True)
    peer.start()
    try:
        await asyncio.wait_for(done.wait(), timeout=3)
        assert outcome == [None]
    finally:
        peer.join(5)
        await srv.stop()


@pytest.mark.asyncio
async def test_cancelled_disconnect_releases_socket():
    ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ctx.load_cert_chain(CERT, KEY)
    listener = socket.create_server(('127.0.0.1', 0))
    release = threading.Event()

    def silent_peer():
        sock, _ = listener.accept()
        with ctx.wrap_socket(sock, server_side=True):
            release.wait(10)

    peer = threading.Thread(target=silent_peer, daemon=True)
    peer.start()
    try:
        conn = SMPPConnection(
            '127.0.0.1',
            listener.getsockname()[1],
            write_timeout=10,
            ssl=ssl.create_default_context(cafile=CERT),
        )
        await conn.connect()
        raw = conn._writer.get_extra_info('socket')
        task = asyncio.create_task(conn.disconnect())
        await asyncio.sleep(0.3)  # let it block on the unanswered close_notify
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        await asyncio.sleep(0.1)
        assert raw.fileno() == -1
    finally:
        release.set()
        peer.join(5)
        listener.close()


def test_plain_by_default():
    assert SMPPConnection('h', 1).ssl is None
