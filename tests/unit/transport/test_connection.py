"""
Unit tests for SMPP Connection module.

Tests the async TCP connection handling, PDU sending/receiving,
connection state tracking, and error handling.
"""

import asyncio
import struct
import time
from unittest.mock import AsyncMock, patch

import pytest

from smpp.exceptions import (
    SMPPConnectionException,
    SMPPPDUException,
    SMPPTimeoutException,
)
from smpp.protocol.constants import PDU_HEADER_SIZE
from smpp.transport.connection import ConnectionState, SMPPConnection


class MockPDU:
    """Mock PDU for testing"""

    def __init__(self, sequence_number: int = 1, command_id: int = 0x80000001):
        self.sequence_number = sequence_number
        self.command_id = command_id
        self.command_status = 0
        self.length = 16

    def encode(self) -> bytes:
        """Return mock encoded PDU"""
        return struct.pack(
            '>LLLL', 16, self.command_id, self.command_status, self.sequence_number
        )


class MockEnquireLink(MockPDU):
    """Mock EnquireLink PDU"""

    def __init__(self):
        super().__init__(command_id=0x00000015)


@pytest.fixture
def mock_reader():
    """Mock asyncio StreamReader"""
    reader = AsyncMock(spec=asyncio.StreamReader)
    # By default, make readexactly raise IncompleteReadError to simulate connection close
    # This prevents the receive loop from trying to read indefinitely from a mock
    reader.readexactly.side_effect = asyncio.IncompleteReadError(b'', 16)
    return reader


@pytest.fixture
def mock_writer():
    """Mock asyncio StreamWriter"""
    writer = AsyncMock(spec=asyncio.StreamWriter)
    writer.get_extra_info.return_value = ('127.0.0.1', 12345)
    return writer


@pytest.fixture
def connection():
    """Create SMPPConnection instance for testing"""
    return SMPPConnection(
        host='localhost',
        port=2775,
        read_timeout=5.0,
        write_timeout=5.0,
        enquire_link_interval=30.0,
        # max_pending_pdus=100,
        # cleanup_interval=60.0,
    )


@pytest.fixture
def connected_connection(mock_reader, mock_writer):
    """Create connected SMPPConnection instance"""
    conn = SMPPConnection('localhost', 2775)
    conn._reader = mock_reader
    conn._writer = mock_writer
    conn._connected = True
    conn._set_state(ConnectionState.OPEN)
    # Don't start background tasks in tests - they cause issues with mocks
    return conn


class TestSMPPConnectionInit:
    """Test SMPPConnection initialization"""

    def test_init_default_values(self):
        """Test initialization with default values"""
        conn = SMPPConnection('localhost', 2775)

        assert conn.host == 'localhost'
        assert conn.port == 2775
        assert conn.read_timeout == 30.0
        assert conn.write_timeout == 30.0
        assert conn.enquire_link_interval == 30.0
        # assert conn.max_pending_pdus == 1000
        # assert conn.cleanup_interval == 300.0
        assert conn.state == ConnectionState.CLOSED
        assert not conn.is_connected
        assert not conn.is_bound
        assert conn._sequence_counter == 1
        assert len(conn._pending_pdus) == 0

    def test_init_custom_values(self):
        """Test initialization with custom values"""
        conn = SMPPConnection(
            host='example.com',
            port=9999,
            read_timeout=10.0,
            write_timeout=15.0,
            enquire_link_interval=45.0,
            # max_pending_pdus=500,
            # cleanup_interval=120.0,
        )

        assert conn.host == 'example.com'
        assert conn.port == 9999
        assert conn.read_timeout == 10.0
        assert conn.write_timeout == 15.0
        assert conn.enquire_link_interval == 45.0
        # assert conn.max_pending_pdus == 500
        # assert conn.cleanup_interval == 120.0


class TestConnectionProperties:
    """Test connection properties and state management"""

    def test_state_property(self, connection):
        """Test state property getter"""
        assert connection.state == ConnectionState.CLOSED
        connection._state = ConnectionState.OPEN
        assert connection.state == ConnectionState.OPEN

    def test_is_connected_property(self, connection, mock_writer):
        """Test is_connected property"""
        assert not connection.is_connected

        connection._connected = True
        connection._writer = mock_writer
        assert connection.is_connected

        connection._writer = None
        assert not connection.is_connected

    def test_is_bound_property(self, connection):
        """Test is_bound property"""
        assert not connection.is_bound

        connection._state = ConnectionState.BOUND_TX
        assert connection.is_bound

        connection._state = ConnectionState.BOUND_RX
        assert connection.is_bound

        connection._state = ConnectionState.BOUND_TRX
        assert connection.is_bound

        connection._state = ConnectionState.OPEN
        assert not connection.is_bound

    def test_set_state_with_handler(self, connection):
        """Test state change with handler"""
        state_changes = []

        def state_handler(old_state, new_state):
            state_changes.append((old_state, new_state))

        connection.on_state_changed = state_handler
        connection._set_state(ConnectionState.OPEN)

        assert len(state_changes) == 1
        assert state_changes[0] == (ConnectionState.CLOSED, ConnectionState.OPEN)

    def test_set_state_handler_exception(self, connection):
        """Test state change handler exception handling"""

        def failing_handler(old_state, new_state):
            raise ValueError('Handler error')

        connection.on_state_changed = failing_handler

        # Should not raise exception
        connection._set_state(ConnectionState.OPEN)
        assert connection.state == ConnectionState.OPEN


class TestSequenceNumber:
    """Test sequence number generation"""

    def test_get_next_sequence(self, connection):
        """Test sequence number generation"""
        assert connection._get_next_sequence() == 1
        assert connection._get_next_sequence() == 2
        assert connection._get_next_sequence() == 3

    def test_sequence_wraparound(self, connection):
        """Test sequence number wraparound"""
        connection._sequence_counter = 0x7FFFFFFE

        assert connection._get_next_sequence() == 0x7FFFFFFE
        assert connection._get_next_sequence() == 0x7FFFFFFF
        assert connection._get_next_sequence() == 1  # Wraps to 1, not 0


class TestConnection:
    """Test connection establishment and teardown"""

    @pytest.mark.asyncio
    async def test_connect_success(self, connection, mock_reader, mock_writer):
        """Test successful connection"""
        with patch('asyncio.open_connection', new_callable=AsyncMock) as mock_open:
            mock_open.return_value = (mock_reader, mock_writer)

            # Make mock_reader raise an exception to simulate connection close
            # This prevents the receive loop from trying to read from the mock
            mock_reader.readexactly.side_effect = asyncio.IncompleteReadError(b'', 16)

            await connection.connect()

            assert connection.is_connected
            assert connection.state == ConnectionState.OPEN
            assert connection._reader == mock_reader
            assert connection._writer == mock_writer
            mock_open.assert_called_once_with('localhost', 2775)

            # Clean up background tasks
            await connection.disconnect()

    @pytest.mark.asyncio
    async def test_connect_already_connected(self, connected_connection):
        """Test connect when already connected"""
        with pytest.raises(SMPPConnectionException, match='Already connected'):
            await connected_connection.connect()

    @pytest.mark.asyncio
    async def test_connect_timeout(self, connection):
        """Test connection timeout"""
        with patch('asyncio.open_connection', new_callable=AsyncMock) as mock_open:
            mock_open.side_effect = asyncio.TimeoutError()

            with pytest.raises(SMPPTimeoutException, match='Connection timeout'):
                await connection.connect()

    @pytest.mark.asyncio
    async def test_connect_failure(self, connection):
        """Test connection failure"""
        with patch('asyncio.open_connection', new_callable=AsyncMock) as mock_open:
            mock_open.side_effect = OSError('Connection refused')

            with pytest.raises(SMPPConnectionException, match='Failed to connect'):
                await connection.connect()

    @pytest.mark.asyncio
    async def test_disconnect_not_connected(self, connection):
        """Test disconnect when not connected"""
        # Should not raise exception
        await connection.disconnect()

    @pytest.mark.asyncio
    async def test_disconnect_success(self, connected_connection):
        """Test successful disconnection"""
        # Add some pending PDUs
        future1 = asyncio.Future()
        future2 = asyncio.Future()
        connected_connection._pending_pdus = {
            1: (future1, time.time()),
            2: (future2, time.time()),
        }

        await connected_connection.disconnect()

        assert not connected_connection.is_connected
        assert connected_connection.state == ConnectionState.CLOSED
        assert connected_connection._reader is None
        assert connected_connection._writer is None
        assert len(connected_connection._pending_pdus) == 0

        # Pending PDUs should be completed with exception
        assert future1.done()
        assert future2.done()
        assert isinstance(future1.exception(), SMPPConnectionException)
        assert isinstance(future2.exception(), SMPPConnectionException)


class TestPDUSending:
    """Test PDU sending functionality"""

    @pytest.mark.asyncio
    async def test_send_pdu_not_connected(self, connection):
        """Test sending PDU when not connected"""
        pdu = MockPDU()

        with pytest.raises(SMPPConnectionException, match='Not connected'):
            await connection.send_pdu(pdu)

    @pytest.mark.asyncio
    async def test_send_pdu_no_response(self, connected_connection):
        """Test sending PDU without waiting for response"""
        pdu = MockPDU(sequence_number=0)  # Will get auto-assigned

        result = await connected_connection.send_pdu(pdu, wait_response=False)

        assert result is None
        assert pdu.sequence_number == 1  # Auto-assigned
        connected_connection._writer.write.assert_called_once()
        connected_connection._writer.drain.assert_called_once()

        # Ensure clean shutdown to avoid task warnings
        await connected_connection.disconnect()

    @pytest.mark.asyncio
    async def test_send_pdu_with_response(self, connected_connection):
        """Test sending PDU with response"""
        pdu = MockPDU(sequence_number=0)
        response_pdu = MockPDU(sequence_number=1)

        # Mock the response
        async def mock_wait_for(future, timeout):
            if isinstance(future, asyncio.Future):
                future.set_result(response_pdu)
                return response_pdu
            return await future

        with patch('asyncio.wait_for', side_effect=mock_wait_for):
            result = await connected_connection.send_pdu(pdu, wait_response=True)

        assert result == response_pdu
        assert pdu.sequence_number == 1

    @pytest.mark.asyncio
    async def test_send_pdu_response_timeout(self, connected_connection):
        """Test PDU response timeout"""
        pdu = MockPDU(sequence_number=0)

        with patch('asyncio.wait_for', side_effect=asyncio.TimeoutError):
            with pytest.raises(SMPPTimeoutException, match='Response timeout'):
                await connected_connection.send_pdu(pdu, wait_response=True)

    @pytest.mark.asyncio
    async def test_send_data_failure(self, connected_connection):
        """Test send data failure"""
        pdu = MockPDU()

        # Create a custom drain function that raises an exception
        async def failing_drain():
            raise OSError('Send failed')

        # Replace the drain method with our failing version
        connected_connection._writer.drain = failing_drain

        with pytest.raises(SMPPConnectionException, match='Failed to send PDU'):
            await connected_connection.send_pdu(pdu, wait_response=False)


class TestPDUReceiving:
    """Test PDU receiving functionality"""

    @pytest.mark.asyncio
    async def test_receive_pdu_success(self, connected_connection, mock_reader):
        """Test successful PDU reception"""
        # Mock PDU data
        pdu_data = struct.pack('>LLLL', 16, 0x80000001, 0, 123)
        mock_reader.readexactly.side_effect = [
            pdu_data[:PDU_HEADER_SIZE],  # Header
            pdu_data[PDU_HEADER_SIZE:],  # Body (empty in this case)
        ]

        with patch('smpp.transport.connection.decode_pdu') as mock_decode:
            mock_pdu = MockPDU(sequence_number=123)
            mock_decode.return_value = mock_pdu

            result = await connected_connection._receive_pdu()

            assert result == mock_pdu
            mock_decode.assert_called_once_with(pdu_data)

    @pytest.mark.asyncio
    async def test_receive_pdu_no_reader(self, connected_connection):
        """Test PDU reception with no reader"""
        connected_connection._reader = None

        result = await connected_connection._receive_pdu()
        assert result is None

    @pytest.mark.asyncio
    async def test_receive_pdu_timeout(self, connected_connection, mock_reader):
        """Test PDU reception timeout"""
        mock_reader.readexactly.side_effect = asyncio.TimeoutError()

        with pytest.raises(SMPPTimeoutException, match='PDU receive timeout'):
            await connected_connection._receive_pdu()

    @pytest.mark.asyncio
    async def test_receive_pdu_incomplete_read(self, connected_connection, mock_reader):
        """Test incomplete PDU read"""
        mock_reader.readexactly.side_effect = asyncio.IncompleteReadError(b'', 16)

        with pytest.raises(SMPPConnectionException, match='Connection closed by peer'):
            await connected_connection._receive_pdu()

    @pytest.mark.asyncio
    async def test_receive_pdu_invalid_length(self, connected_connection, mock_reader):
        """Test PDU with invalid length"""
        # PDU with length < header size
        pdu_data = struct.pack('>LLLL', 4, 0x80000001, 0, 123)
        # Override the default side effect for this test
        mock_reader.readexactly.side_effect = None
        mock_reader.readexactly.return_value = pdu_data[:PDU_HEADER_SIZE]

        with pytest.raises(SMPPPDUException, match='Invalid PDU length'):
            await connected_connection._receive_pdu()

    @pytest.mark.asyncio
    async def test_handle_received_pdu_response(self, connected_connection):
        """Test handling received PDU as response"""
        # Set up pending PDU
        future = asyncio.Future()
        connected_connection._pending_pdus[123] = (future, time.time())

        response_pdu = MockPDU(sequence_number=123)
        await connected_connection._handle_received_pdu(response_pdu)

        assert future.done()
        assert future.result() == response_pdu
        assert 123 not in connected_connection._pending_pdus

    @pytest.mark.asyncio
    async def test_handle_received_pdu_incoming(self, connected_connection):
        """Test handling received PDU as incoming"""
        received_pdus = []

        def pdu_handler(pdu):
            received_pdus.append(pdu)

        connected_connection.on_pdu_received = pdu_handler

        incoming_pdu = MockPDU(sequence_number=456)
        await connected_connection._handle_received_pdu(incoming_pdu)

        assert len(received_pdus) == 1
        assert received_pdus[0] == incoming_pdu


class TestBackgroundTasks:
    """Test background task functionality"""

    @pytest.mark.asyncio
    async def test_enquire_link_loop(self, connected_connection):
        """Test enquire link loop"""
        connected_connection.enquire_link_interval = 0.1  # Short interval for testing

        with patch('smpp.transport.connection.EnquireLink', MockEnquireLink):
            with patch.object(
                connected_connection, 'send_pdu', new_callable=AsyncMock
            ) as mock_send:
                # Start the loop
                task = asyncio.create_task(connected_connection._enquire_link_loop())

                # Wait a bit for enquire_link to be sent
                await asyncio.sleep(0.2)

                # Cancel the task
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

                # Should have sent at least one enquire_link
                assert mock_send.call_count >= 1

    @pytest.mark.asyncio
    async def test_cleanup_loop(self, connected_connection):
        """Test cleanup loop"""
        connected_connection.cleanup_interval = 0.1  # Short interval for testing

        # Add a stale PDU
        old_time = time.time() - 1000  # Very old timestamp
        future = asyncio.Future()
        connected_connection._pending_pdus[999] = (future, old_time)

        # Start cleanup loop
        task = asyncio.create_task(connected_connection._cleanup_loop())

        # Wait for cleanup
        await asyncio.sleep(0.2)

        # Cancel the task
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

        # Stale PDU should be cleaned up
        assert 999 not in connected_connection._pending_pdus
        assert future.done()
        assert isinstance(future.exception(), SMPPTimeoutException)


class TestMemoryManagement:
    """Test memory management and limits"""

    def test_check_memory_limits(self, connected_connection):
        """Test memory limit enforcement"""
        connected_connection.max_pending_pdus = 10

        # Fill up to the limit
        for i in range(15):  # Exceed the limit
            future = asyncio.Future()
            connected_connection._pending_pdus[i] = (
                future,
                time.time() - i,
            )  # Different timestamps

        connected_connection._check_memory_limits()

        # Should have removed some PDUs
        assert len(connected_connection._pending_pdus) < 15
        assert (
            len(connected_connection._pending_pdus)
            <= connected_connection.max_pending_pdus
        )


class TestBindingStates:
    """Test connection binding state management"""

    def test_set_bound_state_transmitter(self, connection):
        """Test setting transmitter bound state"""
        connection.set_bound_state('transmitter')
        assert connection.state == ConnectionState.BOUND_TX
        assert connection.is_bound

    def test_set_bound_state_receiver(self, connection):
        """Test setting receiver bound state"""
        connection.set_bound_state('receiver')
        assert connection.state == ConnectionState.BOUND_RX
        assert connection.is_bound

    def test_set_bound_state_transceiver(self, connection):
        """Test setting transceiver bound state"""
        connection.set_bound_state('transceiver')
        assert connection.state == ConnectionState.BOUND_TRX
        assert connection.is_bound

    def test_set_bound_state_invalid(self, connection):
        """Test setting invalid bound state"""
        original_state = connection.state
        connection.set_bound_state('invalid')
        assert connection.state == original_state  # Should not change


class TestErrorHandling:
    """Test error handling"""

    @pytest.mark.asyncio
    async def test_handle_connection_error(self, connected_connection):
        """Test connection error handling"""
        error_events = []

        def error_handler(error):
            error_events.append(error)

        connected_connection.on_connection_lost = error_handler

        test_error = OSError('Connection lost')
        await connected_connection._handle_connection_error(test_error)

        assert len(error_events) == 1
        assert error_events[0] == test_error
        assert not connected_connection.is_connected

    @pytest.mark.asyncio
    async def test_handle_connection_error_handler_exception(
        self, connected_connection
    ):
        """Test connection error handler exception"""

        def failing_handler(error):
            raise ValueError('Handler failed')

        connected_connection.on_connection_lost = failing_handler

        # Should not raise exception
        await connected_connection._handle_connection_error(OSError('Test error'))
        assert not connected_connection.is_connected


class TestContextManager:
    """Test async context manager functionality"""

    @pytest.mark.asyncio
    async def test_context_manager_success(self, mock_reader, mock_writer):
        """Test successful context manager usage"""
        with patch('asyncio.open_connection', new_callable=AsyncMock) as mock_open:
            mock_open.return_value = (mock_reader, mock_writer)

            async with SMPPConnection('localhost', 2775) as conn:
                assert conn.is_connected
                assert conn.state == ConnectionState.OPEN

            # Should be disconnected after exiting context
            assert not conn.is_connected
            assert conn.state == ConnectionState.CLOSED

    @pytest.mark.asyncio
    async def test_context_manager_exception(self, mock_reader, mock_writer):
        """Test context manager with exception"""
        with patch('asyncio.open_connection', new_callable=AsyncMock) as mock_open:
            mock_open.return_value = (mock_reader, mock_writer)

            try:
                async with SMPPConnection('localhost', 2775) as conn:
                    assert conn.is_connected
                    raise ValueError('Test exception')
            except ValueError:
                pass

            # Should still be disconnected after exception
            assert not conn.is_connected
            assert conn.state == ConnectionState.CLOSED


class TestRepr:
    """Test string representation"""

    def test_repr(self, connection):
        """Test __repr__ method"""
        repr_str = repr(connection)
        assert 'SMPPConnection' in repr_str
        assert 'host=localhost' in repr_str
        assert 'port=2775' in repr_str
        assert 'state=CLOSED' in repr_str


if __name__ == '__main__':
    pytest.main([__file__])
