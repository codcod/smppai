"""
Integration tests for SMPP Server and Client shutdown interaction

These tests verify the complete shutdown flow between server and client,
ensuring proper notification handling and graceful disconnection.
"""

import asyncio
import pytest
from unittest.mock import Mock

from examples.client import SMSClient
from examples.server import SMSCServer


@pytest.mark.integration
class TestShutdownIntegration:
    """Integration tests for server-client shutdown interaction"""

    @pytest.fixture(autouse=True)
    async def cleanup_after_test(self):
        """Ensure clean state after each test."""
        yield
        # Cancel any remaining tasks
        tasks = [t for t in asyncio.all_tasks() if not t.done()]
        for task in tasks:
            if not task.done():
                task.cancel()
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    @pytest.mark.asyncio
    async def test_server_client_shutdown_integration(self):
        """Test complete server-client shutdown interaction."""
        # Create server with fast timeouts for testing
        server = SMSCServer(host='127.0.0.1', port=0)
        server.server.configure_shutdown(
            grace_period=0.5,  # 500ms
            reminder_delay=0.2,  # 200ms
            shutdown_timeout=0.5,  # 500ms
        )

        # Start server
        await server.start()
        actual_port = server.server._server.sockets[0].getsockname()[1]

        # Create and connect client
        client = SMSClient('127.0.0.1', actual_port, 'test_client', 'password')

        try:
            await client.connect_and_bind()

            # Verify client is connected
            assert client.client.is_connected
            assert client.client.is_bound

            # Send a test message
            message_id = await client.send_sms(
                '12345', '67890', 'Test message before shutdown'
            )
            assert message_id is not None

            # Give server time to process message
            await asyncio.sleep(0.1)

            # Trigger server shutdown
            shutdown_task = asyncio.create_task(server.stop())

            # Wait for client to detect shutdown and disconnect gracefully
            # The client should receive shutdown notification and disconnect within grace period
            await asyncio.sleep(1.0)  # Wait for full shutdown sequence

            # Verify client received shutdown notification and disconnected
            assert client.shutdown_requested or not client.client.is_connected

            # Wait for server shutdown to complete
            await shutdown_task

            assert not server.server.is_running

        finally:
            # Cleanup
            try:
                await client.disconnect()
            except Exception:
                pass
            try:
                await server.stop()
            except Exception:
                pass

    @pytest.mark.asyncio
    async def test_multiple_clients_shutdown(self):
        """Test shutdown with multiple connected clients."""
        # Create server
        server = SMSCServer(host='127.0.0.1', port=0)
        server.server.configure_shutdown(
            grace_period=0.3, reminder_delay=0.2, shutdown_timeout=0.5
        )

        await server.start()
        actual_port = server.server._server.sockets[0].getsockname()[1]

        # Create multiple clients
        clients = []
        for i in range(3):
            client = SMSClient('127.0.0.1', actual_port, f'client_{i}', 'password')
            await client.connect_and_bind()
            clients.append(client)

        try:
            # Verify all clients are connected
            for client in clients:
                assert client.client.is_connected
                assert client.client.is_bound

            # Trigger server shutdown
            start_time = asyncio.get_event_loop().time()
            shutdown_task = asyncio.create_task(server.stop())

            # Wait for shutdown to complete
            await shutdown_task

            shutdown_time = asyncio.get_event_loop().time() - start_time

            # Verify shutdown took at least the grace period
            assert shutdown_time >= 0.3, f'Shutdown too fast: {shutdown_time:.3f}s'

            # All clients should have been notified and disconnected
            for client in clients:
                assert client.shutdown_requested or not client.client.is_connected

        finally:
            # Cleanup
            for client in clients:
                try:
                    await client.disconnect()
                except Exception:
                    pass
            try:
                await server.stop()
            except Exception:
                pass

    @pytest.mark.asyncio
    async def test_client_reconnection_after_server_restart(self):
        """Test that client can reconnect after server restart."""
        # Create server
        server = SMSCServer(host='127.0.0.1', port=0)
        server.server.configure_shutdown(
            grace_period=0.2, reminder_delay=0.1, shutdown_timeout=0.3
        )

        await server.start()
        actual_port = server.server._server.sockets[0].getsockname()[1]

        # Create client
        client = SMSClient('127.0.0.1', actual_port, 'test_client', 'password')
        await client.connect_and_bind()

        # Verify initial connection
        assert client.client.is_connected

        # Shutdown server
        await server.stop()

        # Wait for client to detect disconnection
        await asyncio.sleep(0.5)

        # Verify client detected shutdown
        assert not client.client.is_connected or client.shutdown_requested

        # Restart server (create new instance on same port)
        server = SMSCServer(host='127.0.0.1', port=actual_port)
        await server.start()

        try:
            # Create new client connection
            client = SMSClient('127.0.0.1', actual_port, 'test_client', 'password')
            await client.connect_and_bind()

            # Verify reconnection works
            assert client.client.is_connected
            assert client.client.is_bound

            # Send message to verify functionality
            message_id = await client.send_sms('12345', '67890', 'Test after restart')
            assert message_id is not None

        finally:
            try:
                await client.disconnect()
            except Exception:
                pass
            try:
                await server.stop()
            except Exception:
                pass


@pytest.mark.performance
class TestShutdownPerformance:
    """Performance tests for shutdown operations"""

    @pytest.mark.asyncio
    async def test_shutdown_performance_with_many_clients(self):
        """Test shutdown performance with many concurrent clients."""
        server = SMSCServer(host='127.0.0.1', port=0)
        server.server.configure_shutdown(
            grace_period=0.5, reminder_delay=0.2, shutdown_timeout=1.0
        )

        await server.start()
        actual_port = server.server._server.sockets[0].getsockname()[1]

        # Create mock clients (simplified for performance testing)
        from smpp.server.server import ClientSession
        from smpp.transport import SMPPConnection
        from unittest.mock import AsyncMock

        clients = []
        for i in range(50):  # 50 clients for performance test
            mock_connection = Mock(spec=SMPPConnection)
            mock_connection.disconnect = AsyncMock()
            mock_connection.send_pdu = AsyncMock()
            mock_connection.is_connected = True
            mock_connection.host = '127.0.0.1'
            mock_connection.port = actual_port

            session = ClientSession(
                connection=mock_connection,
                system_id=f'client_{i}',
                bind_type='transceiver',
                bound=True,
            )
            server.server._clients[f'client_{i}'] = session
            clients.append(session)

        try:
            # Measure shutdown time
            import time

            start_time = time.time()
            await server.stop()
            shutdown_time = time.time() - start_time

            # Should complete within reasonable time even with many clients
            assert shutdown_time < 3.0, f'Shutdown took too long: {shutdown_time:.2f}s'

            # Verify all clients received shutdown notifications
            for session in clients:
                session.connection.send_pdu.assert_called()

        finally:
            await server.stop()
