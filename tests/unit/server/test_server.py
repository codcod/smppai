"""
Unit tests for SMPP Server implementation

This module contains tests for the SMPPServer class and ClientSession dataclass.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch

from smpp.exceptions import SMPPException
from smpp.protocol import (
    BindReceiver,
    BindTransceiver,
    BindTransmitter,
    BindTransmitterResp,
    CommandStatus,
    DataCoding,
    DeliverSm,
    EnquireLink,
    EnquireLinkResp,
    GenericNack,
    SubmitSm,
    SubmitSmResp,
    TonType,
    NpiType,
    Unbind,
    UnbindResp,
)
from smpp.server.server import ClientSession, SMPPServer
from smpp.transport import ConnectionState, SMPPConnection


class TestClientSession:
    """Tests for ClientSession dataclass."""

    def test_client_session_init_default(self):
        """Test ClientSession initialization with default values."""
        connection = Mock(spec=SMPPConnection)
        session = ClientSession(connection=connection)

        assert session.connection is connection
        assert session.system_id == ''
        assert session.bind_type == ''
        assert session.bound is False
        assert session.address_range == ''
        assert session.message_counter == 0

    def test_client_session_init_custom(self):
        """Test ClientSession initialization with custom values."""
        connection = Mock(spec=SMPPConnection)
        session = ClientSession(
            connection=connection,
            system_id='test_client',
            bind_type='transmitter',
            bound=True,
            address_range='12345',
            message_counter=5,
        )

        assert session.connection is connection
        assert session.system_id == 'test_client'
        assert session.bind_type == 'transmitter'
        assert session.bound is True
        assert session.address_range == '12345'
        assert session.message_counter == 5


class TestSMPPServerInitialization:
    """Tests for SMPPServer initialization."""

    def test_init_default_values(self):
        """Test server initialization with default values."""
        server = SMPPServer()

        assert server.host == 'localhost'
        assert server.port == 2775
        assert server.system_id == 'SMSC'
        assert server.interface_version == 0x34
        assert server.max_connections == 100
        assert server._server is None
        assert server._running is False
        assert server._clients == {}
        assert server._message_id_counter == 1
        assert server.authenticate is not None

    def test_init_custom_values(self):
        """Test server initialization with custom values."""
        server = SMPPServer(
            host='0.0.0.0',
            port=9999,
            system_id='CustomSMSC',
            interface_version=0x50,
            max_connections=50,
        )

        assert server.host == '0.0.0.0'
        assert server.port == 9999
        assert server.system_id == 'CustomSMSC'
        assert server.interface_version == 0x50
        assert server.max_connections == 50

    def test_default_authenticate(self):
        """Test default authentication method."""
        server = SMPPServer()
        result = server._default_authenticate('test_id', 'test_pass', 'test_type')
        assert result is True


class TestSMPPServerProperties:
    """Tests for SMPPServer properties."""

    def test_is_running_false_initially(self):
        """Test that server is not running initially."""
        server = SMPPServer()
        assert server.is_running is False

    def test_is_running_true_when_started(self):
        """Test that server reports running when started."""
        server = SMPPServer()
        server._running = True
        server._server = Mock()
        assert server.is_running is True

    def test_client_count_empty(self):
        """Test client count when no clients connected."""
        server = SMPPServer()
        assert server.client_count == 0

    def test_client_count_with_clients(self):
        """Test client count with connected clients."""
        server = SMPPServer()
        server._clients = {'client1': Mock(), 'client2': Mock()}
        assert server.client_count == 2


class TestSMPPServerStartStop:
    """Tests for server start/stop functionality."""

    @pytest.mark.asyncio
    async def test_start_success(self):
        """Test successful server start."""
        server = SMPPServer()
        mock_server = Mock()

        with patch('asyncio.start_server', return_value=mock_server):
            await server.start()

        assert server._running is True
        assert server._server is mock_server

    @pytest.mark.asyncio
    async def test_start_already_running(self):
        """Test starting server when already running raises exception."""
        server = SMPPServer()
        server._running = True
        server._server = Mock()

        with pytest.raises(SMPPException, match='Server is already running'):
            await server.start()

    @pytest.mark.asyncio
    async def test_stop_success(self):
        """Test successful server stop."""
        server = SMPPServer()
        mock_server = AsyncMock()
        server._server = mock_server
        server._running = True

        # Add mock client
        mock_connection = AsyncMock()
        session = ClientSession(connection=mock_connection)
        server._clients = {'client1': session}

        await server.stop()

        assert server._running is False
        assert server._server is None
        assert server._clients == {}
        mock_server.close.assert_called_once()
        mock_server.wait_closed.assert_called_once()
        mock_connection.disconnect.assert_called_once()

    @pytest.mark.asyncio
    async def test_stop_not_running(self):
        """Test stopping server when not running."""
        server = SMPPServer()
        # Should not raise exception
        await server.stop()


class TestSMPPServerMessageHandling:
    """Tests for server message handling."""

    def test_get_next_message_id(self):
        """Test message ID generation."""
        server = SMPPServer()

        # First ID should be "1"
        msg_id1 = server._get_next_message_id()
        assert msg_id1 == '1'
        assert server._message_id_counter == 2

        # Second ID should be "2"
        msg_id2 = server._get_next_message_id()
        assert msg_id2 == '2'
        assert server._message_id_counter == 3

    def test_get_client_sessions(self):
        """Test getting all client sessions."""
        server = SMPPServer()
        session1 = Mock()
        session2 = Mock()
        server._clients = {'client1': session1, 'client2': session2}

        sessions = server.get_client_sessions()
        assert len(sessions) == 2
        assert session1 in sessions
        assert session2 in sessions

    def test_get_bound_clients(self):
        """Test getting only bound client sessions."""
        server = SMPPServer()

        bound_session = Mock()
        bound_session.bound = True

        unbound_session = Mock()
        unbound_session.bound = False

        server._clients = {
            'bound_client': bound_session,
            'unbound_client': unbound_session,
        }

        bound_clients = server.get_bound_clients()
        assert len(bound_clients) == 1
        assert bound_session in bound_clients
        assert unbound_session not in bound_clients


class TestSMPPServerContextManager:
    """Tests for server async context manager."""

    @pytest.mark.asyncio
    async def test_context_manager_success(self):
        """Test successful context manager usage."""
        server = SMPPServer()

        with (
            patch.object(server, 'start') as mock_start,
            patch.object(server, 'stop') as mock_stop,
        ):
            async with server:
                pass

            mock_start.assert_called_once()
            mock_stop.assert_called_once()

    @pytest.mark.asyncio
    async def test_context_manager_exception(self):
        """Test context manager with exception."""
        server = SMPPServer()

        with (
            patch.object(server, 'start') as mock_start,
            patch.object(server, 'stop') as mock_stop,
        ):
            with pytest.raises(ValueError):
                async with server:
                    raise ValueError('Test exception')

            mock_start.assert_called_once()
            mock_stop.assert_called_once()


class TestSMPPServerRepr:
    """Tests for server string representation."""

    def test_repr(self):
        """Test server string representation."""
        server = SMPPServer(host='127.0.0.1', port=8080)
        server._clients = {'client1': Mock()}

        repr_str = repr(server)
        assert 'SMPPServer' in repr_str
        assert 'host=127.0.0.1' in repr_str
        assert 'port=8080' in repr_str
        assert 'clients=1' in repr_str


class TestSMPPServerEventHandlers:
    """Tests for server event handler initialization."""

    def test_event_handlers_initialization(self):
        """Test that event handlers are initialized to None."""
        server = SMPPServer()

        assert server.on_client_connected is None
        assert server.on_client_disconnected is None
        assert server.on_client_bound is None
        assert server.on_message_received is None

    def test_set_event_handlers(self):
        """Test setting custom event handlers."""
        server = SMPPServer()

        def mock_connected_handler(server, session):
            pass

        def mock_disconnected_handler(server, session):
            pass

        def mock_bound_handler(server, session):
            pass

        def mock_message_handler(server, session, pdu):
            return 'custom_id'

        server.on_client_connected = mock_connected_handler
        server.on_client_disconnected = mock_disconnected_handler
        server.on_client_bound = mock_bound_handler
        server.on_message_received = mock_message_handler

        assert server.on_client_connected is mock_connected_handler
        assert server.on_client_disconnected is mock_disconnected_handler
        assert server.on_client_bound is mock_bound_handler
        assert server.on_message_received is mock_message_handler


class TestSMPPServerPDUHandling:
    """Test PDU handling through _handle_client_pdu method."""

    def test_handle_bind_transmitter_pdu(self):
        """Test handling of BindTransmitter PDU through PDU handler."""
        server = SMPPServer()
        mock_connection = Mock()
        session = ClientSession(connection=mock_connection)

        pdu = BindTransmitter(
            system_id='test_system',
            password='test_pass',
            interface_version=0x34,
            addr_ton=TonType.NATIONAL,
            addr_npi=NpiType.ISDN,
            address_range='12345',
        )

        # Mock the actual handler to avoid real async calls
        with patch.object(server, '_handle_bind_request') as mock_handler:
            with patch('asyncio.create_task'):
                server._handle_client_pdu(session, pdu)
                mock_handler.assert_called_once()

    def test_handle_bind_receiver_pdu(self):
        """Test handling of BindReceiver PDU through PDU handler."""
        server = SMPPServer()
        mock_connection = Mock()
        session = ClientSession(connection=mock_connection)

        pdu = BindReceiver(
            system_id='test_system',
            password='test_pass',
            interface_version=0x34,
            addr_ton=TonType.NATIONAL,
            addr_npi=NpiType.ISDN,
            address_range='12345',
        )

        with patch.object(server, '_handle_bind_request') as mock_handler:
            with patch('asyncio.create_task'):
                server._handle_client_pdu(session, pdu)
                mock_handler.assert_called_once()

    def test_handle_bind_transceiver_pdu(self):
        """Test handling of BindTransceiver PDU through PDU handler."""
        server = SMPPServer()
        mock_connection = Mock()
        session = ClientSession(connection=mock_connection)

        pdu = BindTransceiver(
            system_id='test_system',
            password='test_pass',
            interface_version=0x34,
            addr_ton=TonType.NATIONAL,
            addr_npi=NpiType.ISDN,
            address_range='12345',
        )

        with patch.object(server, '_handle_bind_request') as mock_handler:
            with patch('asyncio.create_task'):
                server._handle_client_pdu(session, pdu)
                mock_handler.assert_called_once()

    def test_handle_unbind_pdu(self):
        """Test handling of Unbind PDU through PDU handler."""
        server = SMPPServer()
        mock_connection = Mock()
        session = ClientSession(connection=mock_connection)
        session.bound = True

        pdu = Unbind()

        with patch.object(server, '_handle_unbind_request') as mock_handler:
            with patch('asyncio.create_task'):
                server._handle_client_pdu(session, pdu)
                mock_handler.assert_called_once()

    def test_handle_submit_sm_pdu(self):
        """Test handling of SubmitSm PDU through PDU handler."""
        server = SMPPServer()
        mock_connection = Mock()
        session = ClientSession(connection=mock_connection)

        pdu = SubmitSm(
            service_type='',
            source_addr_ton=TonType.INTERNATIONAL,
            source_addr_npi=NpiType.ISDN,
            source_addr='1234',
            dest_addr_ton=TonType.NATIONAL,
            dest_addr_npi=NpiType.ISDN,
            destination_addr='5678',
            esm_class=0,
            protocol_id=0,
            priority_flag=0,
            schedule_delivery_time='',
            validity_period='',
            registered_delivery=0,
            replace_if_present_flag=0,
            data_coding=DataCoding.DEFAULT,
            sm_default_msg_id=0,
            short_message=b'Test message',
        )

        with patch.object(server, '_handle_submit_sm') as mock_handler:
            with patch('asyncio.create_task'):
                server._handle_client_pdu(session, pdu)
                mock_handler.assert_called_once()

    def test_handle_enquire_link_pdu(self):
        """Test handling of EnquireLink PDU through PDU handler."""
        server = SMPPServer()
        mock_connection = Mock()
        session = ClientSession(connection=mock_connection)

        pdu = EnquireLink()

        with patch.object(server, '_handle_enquire_link') as mock_handler:
            with patch('asyncio.create_task'):
                server._handle_client_pdu(session, pdu)
                mock_handler.assert_called_once()

    def test_handle_unknown_pdu(self):
        """Test handling of unknown PDU through PDU handler."""
        server = SMPPServer()
        mock_connection = Mock()
        session = ClientSession(connection=mock_connection)

        pdu = Mock()  # Unknown PDU

        with patch.object(server, '_send_generic_nack') as mock_handler:
            with patch('asyncio.create_task'):
                server._handle_client_pdu(session, pdu)
                mock_handler.assert_called_once()


class TestSMPPServerErrorHandling:
    """Tests for server error handling scenarios."""

    def test_handle_pdu_with_exception(self):
        """Test PDU handling when an exception occurs."""
        server = SMPPServer()
        mock_connection = Mock()
        session = ClientSession(connection=mock_connection)

        pdu = BindTransmitter(system_id='test', password='pass')
        pdu.sequence_number = 123  # Add sequence number for generic nack

        # Mock _handle_bind_request to raise an exception
        with patch.object(
            server, '_handle_bind_request', side_effect=Exception('Test error')
        ):
            with patch.object(server, '_send_generic_nack'):
                with patch('asyncio.create_task') as mock_create_task:
                    # First call should raise exception, second call (generic nack) should succeed
                    mock_create_task.side_effect = [Exception('Test error'), Mock()]
                    server._handle_client_pdu(session, pdu)
                    # Should attempt to call generic nack (twice: once failed, once succeeded)
                    assert mock_create_task.call_count == 2

    def test_invalid_pdu_type(self):
        """Test handling of invalid/unknown PDU type."""
        server = SMPPServer()
        mock_connection = Mock()
        session = ClientSession(connection=mock_connection)

        # Create a mock PDU that doesn't match any known type
        pdu = Mock()
        pdu.__class__.__name__ = 'UnknownPDU'
        pdu.sequence_number = 123

        with patch.object(server, '_send_generic_nack'):
            with patch('asyncio.create_task') as mock_create_task:
                server._handle_client_pdu(session, pdu)
                mock_create_task.assert_called_once()


class TestSMPPServerClientConnection:
    """Tests for client connection handling."""

    @pytest.mark.asyncio
    async def test_handle_client_connection_success(self):
        """Test successful client connection handling."""
        server = SMPPServer()

        # Mock stream reader/writer
        mock_reader = AsyncMock()
        mock_writer = AsyncMock()
        mock_writer.get_extra_info = Mock(return_value=('127.0.0.1', 12345))

        # Mock SMPPConnection
        mock_connection = AsyncMock(spec=SMPPConnection)
        mock_connection._receive_loop = AsyncMock()

        with (
            patch('smpp.server.server.SMPPConnection', return_value=mock_connection),
            patch('asyncio.create_task') as mock_create_task,
        ):
            await server._handle_client_connection(mock_reader, mock_writer)

            # Verify connection setup
            assert '127.0.0.1:12345' in server._clients
            session = server._clients['127.0.0.1:12345']
            assert session.connection is mock_connection

            # Verify connection state
            mock_connection._set_state.assert_called_with(ConnectionState.OPEN)
            mock_create_task.assert_called()

    @pytest.mark.asyncio
    async def test_handle_client_connection_max_connections(self):
        """Test client connection rejected when max connections exceeded."""
        server = SMPPServer(max_connections=1)

        # Add existing client
        existing_session = Mock()
        server._clients = {'client1': existing_session}

        # Mock new connection
        mock_reader = AsyncMock()
        mock_writer = AsyncMock()
        mock_writer.get_extra_info = Mock(return_value=('127.0.0.1', 12345))

        await server._handle_client_connection(mock_reader, mock_writer)

        # Verify connection was rejected
        mock_writer.close.assert_called_once()
        mock_writer.wait_closed.assert_called_once()
        assert len(server._clients) == 1  # Only existing client

    @pytest.mark.asyncio
    async def test_handle_client_connection_with_event_handler(self):
        """Test client connection with event handler."""
        server = SMPPServer()
        mock_handler = Mock()
        server.on_client_connected = mock_handler

        mock_reader = AsyncMock()
        mock_writer = AsyncMock()
        mock_writer.get_extra_info = Mock(return_value=('127.0.0.1', 12345))

        mock_connection = AsyncMock(spec=SMPPConnection)

        with (
            patch('smpp.server.server.SMPPConnection', return_value=mock_connection),
            patch('asyncio.create_task'),
        ):
            await server._handle_client_connection(mock_reader, mock_writer)

            # Verify handler was called
            mock_handler.assert_called_once()
            args = mock_handler.call_args[0]
            assert args[0] is server
            assert isinstance(args[1], ClientSession)

    @pytest.mark.asyncio
    async def test_handle_client_connection_handler_exception(self):
        """Test client connection when handler raises exception."""
        server = SMPPServer()
        mock_handler = Mock(side_effect=Exception('Handler error'))
        server.on_client_connected = mock_handler

        mock_reader = AsyncMock()
        mock_writer = AsyncMock()
        mock_writer.get_extra_info = Mock(return_value=('127.0.0.1', 12345))

        mock_connection = AsyncMock(spec=SMPPConnection)

        with (
            patch('smpp.server.server.SMPPConnection', return_value=mock_connection),
            patch('asyncio.create_task'),
        ):
            # Should not raise exception
            await server._handle_client_connection(mock_reader, mock_writer)

            # Client should still be connected
            assert '127.0.0.1:12345' in server._clients

    @pytest.mark.asyncio
    async def test_handle_client_disconnected(self):
        """Test client disconnection handling."""
        server = SMPPServer()
        session = ClientSession(connection=Mock())
        server._clients = {'127.0.0.1:12345': session}

        mock_handler = Mock()
        server.on_client_disconnected = mock_handler

        error = Exception('Connection lost')
        await server._handle_client_disconnected(session, error)

        # Verify client was removed
        assert '127.0.0.1:12345' not in server._clients

        # Verify handler was called
        mock_handler.assert_called_once_with(server, session)

    @pytest.mark.asyncio
    async def test_handle_client_disconnected_handler_exception(self):
        """Test client disconnection when handler raises exception."""
        server = SMPPServer()
        session = ClientSession(connection=Mock())
        server._clients = {'127.0.0.1:12345': session}

        mock_handler = Mock(side_effect=Exception('Handler error'))
        server.on_client_disconnected = mock_handler

        error = Exception('Connection lost')
        # Should not raise exception
        await server._handle_client_disconnected(session, error)

        # Client should still be removed
        assert '127.0.0.1:12345' not in server._clients


class TestSMPPServerBindHandling:
    """Tests for bind request handling."""

    @pytest.mark.asyncio
    async def test_handle_bind_request_transmitter_success(self):
        """Test successful bind transmitter request."""
        server = SMPPServer()
        session = ClientSession(connection=AsyncMock())
        pdu = BindTransmitter(
            sequence_number=1,
            system_id='test_client',
            password='test_pass',
            system_type='test',
            interface_version=0x34,
            addr_ton=0,
            addr_npi=0,
            address_range='',
        )

        await server._handle_bind_request(session, pdu)

        # Verify session was updated
        assert session.system_id == 'test_client'
        assert session.bound is True
        assert session.bind_type == 'transmitter'

        # Verify connection state was set
        session.connection.set_bound_state.assert_called_with('transmitter')

        # Verify response was sent
        session.connection.send_pdu.assert_called_once()
        sent_pdu = session.connection.send_pdu.call_args[0][0]
        assert isinstance(sent_pdu, BindTransmitterResp)
        assert sent_pdu.command_status == CommandStatus.ESME_ROK

    @pytest.mark.asyncio
    async def test_handle_bind_request_receiver_success(self):
        """Test successful bind receiver request."""
        server = SMPPServer()
        session = ClientSession(connection=AsyncMock())
        pdu = BindReceiver(
            sequence_number=1,
            system_id='test_client',
            password='test_pass',
            system_type='test',
            interface_version=0x34,
            addr_ton=0,
            addr_npi=0,
            address_range='',
        )

        await server._handle_bind_request(session, pdu)

        assert session.bind_type == 'receiver'
        session.connection.set_bound_state.assert_called_with('receiver')

    @pytest.mark.asyncio
    async def test_handle_bind_request_transceiver_success(self):
        """Test successful bind transceiver request."""
        server = SMPPServer()
        session = ClientSession(connection=AsyncMock())
        pdu = BindTransceiver(
            sequence_number=1,
            system_id='test_client',
            password='test_pass',
            system_type='test',
            interface_version=0x34,
            addr_ton=0,
            addr_npi=0,
            address_range='',
        )

        await server._handle_bind_request(session, pdu)

        assert session.bind_type == 'transceiver'
        session.connection.set_bound_state.assert_called_with('transceiver')

    @pytest.mark.asyncio
    async def test_handle_bind_request_already_bound(self):
        """Test bind request when already bound."""
        server = SMPPServer()
        session = ClientSession(connection=AsyncMock(), bound=True)
        pdu = BindTransmitter(
            sequence_number=1,
            system_id='test_client',
            password='test_pass',
            system_type='test',
            interface_version=0x34,
            addr_ton=0,
            addr_npi=0,
            address_range='',
        )

        await server._handle_bind_request(session, pdu)

        # Verify error response was sent
        session.connection.send_pdu.assert_called_once()
        sent_pdu = session.connection.send_pdu.call_args[0][0]
        assert sent_pdu.command_status == CommandStatus.ESME_RALYBND

    @pytest.mark.asyncio
    async def test_handle_bind_request_auth_failure(self):
        """Test bind request with authentication failure."""
        server = SMPPServer()
        server.authenticate = Mock(return_value=False)
        session = ClientSession(connection=AsyncMock())
        pdu = BindTransmitter(
            sequence_number=1,
            system_id='test_client',
            password='wrong_pass',
            system_type='test',
            interface_version=0x34,
            addr_ton=0,
            addr_npi=0,
            address_range='',
        )

        await server._handle_bind_request(session, pdu)

        # Verify session was not updated
        assert session.bound is False
        assert session.system_id == ''

        # Verify error response was sent
        session.connection.send_pdu.assert_called_once()
        sent_pdu = session.connection.send_pdu.call_args[0][0]
        assert sent_pdu.command_status == CommandStatus.ESME_RBINDFAIL

    @pytest.mark.asyncio
    async def test_handle_bind_request_with_event_handler(self):
        """Test bind request with event handler."""
        server = SMPPServer()
        mock_handler = Mock()
        server.on_client_bound = mock_handler
        session = ClientSession(connection=AsyncMock())
        pdu = BindTransmitter(
            sequence_number=1,
            system_id='test_client',
            password='test_pass',
            system_type='test',
            interface_version=0x34,
            addr_ton=0,
            addr_npi=0,
            address_range='',
        )

        await server._handle_bind_request(session, pdu)

        # Verify handler was called
        mock_handler.assert_called_once_with(server, session)

    @pytest.mark.asyncio
    async def test_handle_bind_request_handler_exception(self):
        """Test bind request when handler raises exception."""
        server = SMPPServer()
        mock_handler = Mock(side_effect=Exception('Handler error'))
        server.on_client_bound = mock_handler
        session = ClientSession(connection=AsyncMock())
        pdu = BindTransmitter(
            sequence_number=1,
            system_id='test_client',
            password='test_pass',
            system_type='test',
            interface_version=0x34,
            addr_ton=0,
            addr_npi=0,
            address_range='',
        )

        # Should not raise exception
        await server._handle_bind_request(session, pdu)

        # Bind should still succeed
        assert session.bound is True

    @pytest.mark.asyncio
    async def test_handle_bind_request_send_response_exception(self):
        """Test bind request when send response fails."""
        server = SMPPServer()
        session = ClientSession(connection=AsyncMock())
        session.connection.send_pdu.side_effect = Exception('Send failed')
        pdu = BindTransmitter(
            sequence_number=1,
            system_id='test_client',
            password='test_pass',
            system_type='test',
            interface_version=0x34,
            addr_ton=0,
            addr_npi=0,
            address_range='',
        )

        # Should not raise exception
        await server._handle_bind_request(session, pdu)

    @pytest.mark.asyncio
    async def test_handle_bind_request_invalid_pdu_type(self):
        """Test bind request with invalid PDU type."""
        server = SMPPServer()
        session = ClientSession(connection=AsyncMock())
        pdu = Mock()  # Not a bind PDU

        # Should return early without error
        await server._handle_bind_request(session, pdu)

        # No response should be sent
        session.connection.send_pdu.assert_not_called()


class TestSMPPServerUnbindHandling:
    """Tests for unbind request handling."""

    @pytest.mark.asyncio
    async def test_handle_unbind_request_success(self):
        """Test successful unbind request."""
        server = SMPPServer()
        session = ClientSession(
            connection=AsyncMock(),
            system_id='test_client',
            bound=True,
            bind_type='transmitter',
        )
        pdu = Unbind(sequence_number=1)

        await server._handle_unbind_request(session, pdu)

        # Verify session was updated
        assert session.bound is False
        assert session.bind_type == ''

        # Verify response was sent
        session.connection.send_pdu.assert_called_once()
        sent_pdu = session.connection.send_pdu.call_args[0][0]
        assert isinstance(sent_pdu, UnbindResp)
        assert sent_pdu.command_status == CommandStatus.ESME_ROK

        # Verify connection was closed
        session.connection.disconnect.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_unbind_request_exception(self):
        """Test unbind request when exception occurs."""
        server = SMPPServer()
        session = ClientSession(connection=AsyncMock())
        session.connection.send_pdu.side_effect = Exception('Send failed')
        pdu = Unbind(sequence_number=1)

        # Should not raise exception
        await server._handle_unbind_request(session, pdu)


class TestSMPPServerSubmitSmHandling:
    """Tests for submit_sm request handling."""

    @pytest.mark.asyncio
    async def test_handle_submit_sm_success_transmitter(self):
        """Test successful submit_sm from transmitter."""
        server = SMPPServer()
        session = ClientSession(
            connection=AsyncMock(),
            bound=True,
            bind_type='transmitter',
            system_id='test_client',
        )
        pdu = SubmitSm(
            sequence_number=1,
            service_type='',
            source_addr_ton=0,
            source_addr_npi=0,
            source_addr='12345',
            dest_addr_ton=0,
            dest_addr_npi=0,
            destination_addr='67890',
            esm_class=0,
            protocol_id=0,
            priority_flag=0,
            schedule_delivery_time='',
            validity_period='',
            registered_delivery=0,
            replace_if_present_flag=0,
            data_coding=0,
            sm_default_msg_id=0,
            short_message=b'Hello',
        )

        await server._handle_submit_sm(session, pdu)

        # Verify message counter was incremented
        assert session.message_counter == 1

        # Verify response was sent
        session.connection.send_pdu.assert_called_once()
        sent_pdu = session.connection.send_pdu.call_args[0][0]
        assert isinstance(sent_pdu, SubmitSmResp)
        assert sent_pdu.command_status == CommandStatus.ESME_ROK
        assert sent_pdu.message_id == '1'

    @pytest.mark.asyncio
    async def test_handle_submit_sm_success_transceiver(self):
        """Test successful submit_sm from transceiver."""
        server = SMPPServer()
        session = ClientSession(
            connection=AsyncMock(), bound=True, bind_type='transceiver'
        )
        pdu = SubmitSm(
            sequence_number=1,
            service_type='',
            source_addr_ton=0,
            source_addr_npi=0,
            source_addr='12345',
            dest_addr_ton=0,
            dest_addr_npi=0,
            destination_addr='67890',
            esm_class=0,
            protocol_id=0,
            priority_flag=0,
            schedule_delivery_time='',
            validity_period='',
            registered_delivery=0,
            replace_if_present_flag=0,
            data_coding=0,
            sm_default_msg_id=0,
            short_message=b'Hello',
        )

        await server._handle_submit_sm(session, pdu)

        # Verify successful response
        sent_pdu = session.connection.send_pdu.call_args[0][0]
        assert sent_pdu.command_status == CommandStatus.ESME_ROK

    @pytest.mark.asyncio
    async def test_handle_submit_sm_not_bound(self):
        """Test submit_sm when not bound."""
        server = SMPPServer()
        session = ClientSession(connection=AsyncMock(), bound=False)
        pdu = SubmitSm(
            sequence_number=1,
            service_type='',
            source_addr_ton=0,
            source_addr_npi=0,
            source_addr='12345',
            dest_addr_ton=0,
            dest_addr_npi=0,
            destination_addr='67890',
            esm_class=0,
            protocol_id=0,
            priority_flag=0,
            schedule_delivery_time='',
            validity_period='',
            registered_delivery=0,
            replace_if_present_flag=0,
            data_coding=0,
            sm_default_msg_id=0,
            short_message=b'Hello',
        )

        await server._handle_submit_sm(session, pdu)

        # Verify error response
        sent_pdu = session.connection.send_pdu.call_args[0][0]
        assert sent_pdu.command_status == CommandStatus.ESME_RINVBNDSTS

    @pytest.mark.asyncio
    async def test_handle_submit_sm_wrong_bind_type(self):
        """Test submit_sm from receiver (wrong bind type)."""
        server = SMPPServer()
        session = ClientSession(
            connection=AsyncMock(), bound=True, bind_type='receiver'
        )
        pdu = SubmitSm(
            sequence_number=1,
            service_type='',
            source_addr_ton=0,
            source_addr_npi=0,
            source_addr='12345',
            dest_addr_ton=0,
            dest_addr_npi=0,
            destination_addr='67890',
            esm_class=0,
            protocol_id=0,
            priority_flag=0,
            schedule_delivery_time='',
            validity_period='',
            registered_delivery=0,
            replace_if_present_flag=0,
            data_coding=0,
            sm_default_msg_id=0,
            short_message=b'Hello',
        )

        await server._handle_submit_sm(session, pdu)

        # Verify error response
        sent_pdu = session.connection.send_pdu.call_args[0][0]
        assert sent_pdu.command_status == CommandStatus.ESME_RINVBNDSTS

    @pytest.mark.asyncio
    async def test_handle_submit_sm_with_message_handler(self):
        """Test submit_sm with custom message handler."""
        server = SMPPServer()
        mock_handler = Mock(return_value='custom_123')
        server.on_message_received = mock_handler

        session = ClientSession(
            connection=AsyncMock(), bound=True, bind_type='transmitter'
        )
        pdu = SubmitSm(
            sequence_number=1,
            service_type='',
            source_addr_ton=0,
            source_addr_npi=0,
            source_addr='12345',
            dest_addr_ton=0,
            dest_addr_npi=0,
            destination_addr='67890',
            esm_class=0,
            protocol_id=0,
            priority_flag=0,
            schedule_delivery_time='',
            validity_period='',
            registered_delivery=0,
            replace_if_present_flag=0,
            data_coding=0,
            sm_default_msg_id=0,
            short_message=b'Hello',
        )

        await server._handle_submit_sm(session, pdu)

        # Verify handler was called
        mock_handler.assert_called_once_with(server, session, pdu)

        # Verify custom message ID was used
        sent_pdu = session.connection.send_pdu.call_args[0][0]
        assert sent_pdu.message_id == 'custom_123'

    @pytest.mark.asyncio
    async def test_handle_submit_sm_handler_exception(self):
        """Test submit_sm when message handler raises exception."""
        server = SMPPServer()
        mock_handler = Mock(side_effect=Exception('Handler error'))
        server.on_message_received = mock_handler

        session = ClientSession(
            connection=AsyncMock(), bound=True, bind_type='transmitter'
        )
        pdu = SubmitSm(
            sequence_number=1,
            service_type='',
            source_addr_ton=0,
            source_addr_npi=0,
            source_addr='12345',
            dest_addr_ton=0,
            dest_addr_npi=0,
            destination_addr='67890',
            esm_class=0,
            protocol_id=0,
            priority_flag=0,
            schedule_delivery_time='',
            validity_period='',
            registered_delivery=0,
            replace_if_present_flag=0,
            data_coding=0,
            sm_default_msg_id=0,
            short_message=b'Hello',
        )

        # Should not raise exception
        await server._handle_submit_sm(session, pdu)

        # Should still send successful response with default message ID
        sent_pdu = session.connection.send_pdu.call_args[0][0]
        assert sent_pdu.command_status == CommandStatus.ESME_ROK
        assert sent_pdu.message_id == '1'

    @pytest.mark.asyncio
    async def test_handle_submit_sm_send_response_exception(self):
        """Test submit_sm when send response fails."""
        server = SMPPServer()
        session = ClientSession(
            connection=AsyncMock(), bound=True, bind_type='transmitter'
        )
        session.connection.send_pdu.side_effect = Exception('Send failed')

        pdu = SubmitSm(
            sequence_number=1,
            service_type='',
            source_addr_ton=0,
            source_addr_npi=0,
            source_addr='12345',
            dest_addr_ton=0,
            dest_addr_npi=0,
            destination_addr='67890',
            esm_class=0,
            protocol_id=0,
            priority_flag=0,
            schedule_delivery_time='',
            validity_period='',
            registered_delivery=0,
            replace_if_present_flag=0,
            data_coding=0,
            sm_default_msg_id=0,
            short_message=b'Hello',
        )

        # Should not raise exception
        await server._handle_submit_sm(session, pdu)

    @pytest.mark.asyncio
    async def test_handle_submit_sm_general_exception(self):
        """Test submit_sm when general exception occurs."""
        server = SMPPServer()
        session = ClientSession(
            connection=AsyncMock(), bound=True, bind_type='transmitter'
        )

        # Mock to cause exception during processing
        with patch.object(
            server, '_get_next_message_id', side_effect=Exception('Test error')
        ):
            pdu = SubmitSm(
                sequence_number=1,
                service_type='',
                source_addr_ton=0,
                source_addr_npi=0,
                source_addr='12345',
                dest_addr_ton=0,
                dest_addr_npi=0,
                destination_addr='67890',
                esm_class=0,
                protocol_id=0,
                priority_flag=0,
                schedule_delivery_time='',
                validity_period='',
                registered_delivery=0,
                replace_if_present_flag=0,
                data_coding=0,
                sm_default_msg_id=0,
                short_message=b'Hello',
            )

            # Should not raise exception
            await server._handle_submit_sm(session, pdu)

            # Should send error response
            sent_pdu = session.connection.send_pdu.call_args[0][0]
            assert sent_pdu.command_status == CommandStatus.ESME_RSUBMITFAIL


class TestSMPPServerEnquireLinkHandling:
    """Tests for enquire_link request handling."""

    @pytest.mark.asyncio
    async def test_handle_enquire_link_success(self):
        """Test successful enquire_link request."""
        server = SMPPServer()
        session = ClientSession(connection=AsyncMock())
        pdu = EnquireLink(sequence_number=1)

        await server._handle_enquire_link(session, pdu)

        # Verify response was sent
        session.connection.send_pdu.assert_called_once()
        sent_pdu = session.connection.send_pdu.call_args[0][0]
        assert isinstance(sent_pdu, EnquireLinkResp)
        assert sent_pdu.command_status == CommandStatus.ESME_ROK
        assert sent_pdu.sequence_number == 1

    @pytest.mark.asyncio
    async def test_handle_enquire_link_exception(self):
        """Test enquire_link when exception occurs."""
        server = SMPPServer()
        session = ClientSession(connection=AsyncMock())
        session.connection.send_pdu.side_effect = Exception('Send failed')
        pdu = EnquireLink(sequence_number=1)

        # Should not raise exception
        await server._handle_enquire_link(session, pdu)


class TestSMPPServerGenericNack:
    """Tests for generic_nack handling."""

    @pytest.mark.asyncio
    async def test_send_generic_nack_success(self):
        """Test successful generic_nack sending."""
        server = SMPPServer()
        session = ClientSession(connection=AsyncMock())

        await server._send_generic_nack(session, 123, CommandStatus.ESME_RINVCMDID)

        # Verify nack was sent
        session.connection.send_pdu.assert_called_once()
        sent_pdu = session.connection.send_pdu.call_args[0][0]
        assert isinstance(sent_pdu, GenericNack)
        assert sent_pdu.sequence_number == 123
        assert sent_pdu.command_status == CommandStatus.ESME_RINVCMDID

    @pytest.mark.asyncio
    async def test_send_generic_nack_exception(self):
        """Test generic_nack when exception occurs."""
        server = SMPPServer()
        session = ClientSession(connection=AsyncMock())
        session.connection.send_pdu.side_effect = Exception('Send failed')

        # Should not raise exception
        await server._send_generic_nack(session, 123, CommandStatus.ESME_RINVCMDID)


class TestSMPPServerDeliverSm:
    """Tests for deliver_sm functionality."""

    @pytest.mark.asyncio
    async def test_deliver_sm_success(self):
        """Test successful message delivery."""
        server = SMPPServer()

        # Set up target session
        target_connection = AsyncMock()
        target_connection.send_pdu.return_value = Mock(
            command_status=CommandStatus.ESME_ROK
        )
        target_session = ClientSession(
            connection=target_connection,
            system_id='target_client',
            bound=True,
            bind_type='receiver',
        )
        server._clients = {'client1': target_session}

        result = await server.deliver_sm(
            target_system_id='target_client',
            source_addr='12345',
            destination_addr='67890',
            short_message='Hello World',
        )

        assert result is True

        # Verify deliver_sm PDU was sent
        target_connection.send_pdu.assert_called_once()
        sent_pdu = target_connection.send_pdu.call_args[0][0]
        assert isinstance(sent_pdu, DeliverSm)
        assert sent_pdu.source_addr == '12345'
        assert sent_pdu.destination_addr == '67890'
        assert sent_pdu.short_message == b'Hello World'

    @pytest.mark.asyncio
    async def test_deliver_sm_target_not_found(self):
        """Test message delivery when target not found."""
        server = SMPPServer()

        result = await server.deliver_sm(
            target_system_id='nonexistent_client',
            source_addr='12345',
            destination_addr='67890',
            short_message='Hello World',
        )

        assert result is False

    @pytest.mark.asyncio
    async def test_deliver_sm_target_not_bound(self):
        """Test message delivery when target not bound."""
        server = SMPPServer()

        target_session = ClientSession(
            connection=AsyncMock(), system_id='target_client', bound=False
        )
        server._clients = {'client1': target_session}

        result = await server.deliver_sm(
            target_system_id='target_client',
            source_addr='12345',
            destination_addr='67890',
            short_message='Hello World',
        )

        assert result is False

    @pytest.mark.asyncio
    async def test_deliver_sm_wrong_bind_type(self):
        """Test message delivery when target has wrong bind type."""
        server = SMPPServer()

        target_session = ClientSession(
            connection=AsyncMock(),
            system_id='target_client',
            bound=True,
            bind_type='transmitter',  # Wrong type for receiving
        )
        server._clients = {'client1': target_session}

        result = await server.deliver_sm(
            target_system_id='target_client',
            source_addr='12345',
            destination_addr='67890',
            short_message='Hello World',
        )

        assert result is False

    @pytest.mark.asyncio
    async def test_deliver_sm_transceiver_success(self):
        """Test message delivery to transceiver."""
        server = SMPPServer()

        target_connection = AsyncMock()
        target_connection.send_pdu.return_value = Mock(
            command_status=CommandStatus.ESME_ROK
        )
        target_session = ClientSession(
            connection=target_connection,
            system_id='target_client',
            bound=True,
            bind_type='transceiver',
        )
        server._clients = {'client1': target_session}

        result = await server.deliver_sm(
            target_system_id='target_client',
            source_addr='12345',
            destination_addr='67890',
            short_message='Hello World',
        )

        assert result is True

    @pytest.mark.asyncio
    async def test_deliver_sm_error_response(self):
        """Test message delivery with error response."""
        server = SMPPServer()

        target_connection = AsyncMock()
        target_connection.send_pdu.return_value = Mock(
            command_status=CommandStatus.ESME_RINVBNDSTS
        )
        target_session = ClientSession(
            connection=target_connection,
            system_id='target_client',
            bound=True,
            bind_type='receiver',
        )
        server._clients = {'client1': target_session}

        result = await server.deliver_sm(
            target_system_id='target_client',
            source_addr='12345',
            destination_addr='67890',
            short_message='Hello World',
        )

        assert result is False

    @pytest.mark.asyncio
    async def test_deliver_sm_no_response(self):
        """Test message delivery with no response."""
        server = SMPPServer()

        target_connection = AsyncMock()
        target_connection.send_pdu.return_value = None
        target_session = ClientSession(
            connection=target_connection,
            system_id='target_client',
            bound=True,
            bind_type='receiver',
        )
        server._clients = {'client1': target_session}

        result = await server.deliver_sm(
            target_system_id='target_client',
            source_addr='12345',
            destination_addr='67890',
            short_message='Hello World',
        )

        assert result is False

    @pytest.mark.asyncio
    async def test_deliver_sm_exception(self):
        """Test message delivery when exception occurs."""
        server = SMPPServer()

        target_connection = AsyncMock()
        target_connection.send_pdu.side_effect = Exception('Send failed')
        target_session = ClientSession(
            connection=target_connection,
            system_id='target_client',
            bound=True,
            bind_type='receiver',
        )
        server._clients = {'client1': target_session}

        result = await server.deliver_sm(
            target_system_id='target_client',
            source_addr='12345',
            destination_addr='67890',
            short_message='Hello World',
        )

        assert result is False

    @pytest.mark.asyncio
    async def test_deliver_sm_with_all_parameters(self):
        """Test message delivery with all parameters."""
        server = SMPPServer()

        target_connection = AsyncMock()
        target_connection.send_pdu.return_value = Mock(
            command_status=CommandStatus.ESME_ROK
        )
        target_session = ClientSession(
            connection=target_connection,
            system_id='target_client',
            bound=True,
            bind_type='receiver',
        )
        server._clients = {'client1': target_session}

        result = await server.deliver_sm(
            target_system_id='target_client',
            source_addr='12345',
            destination_addr='67890',
            short_message='Hello World',
            source_addr_ton=TonType.INTERNATIONAL,
            source_addr_npi=NpiType.ISDN,
            dest_addr_ton=TonType.NATIONAL,
            dest_addr_npi=NpiType.TELEX,
            service_type='SMS',
            esm_class=0x01,
            protocol_id=0x02,
            priority_flag=0x03,
            data_coding=DataCoding.UCS2,
        )

        assert result is True

        # Verify PDU parameters
        sent_pdu = target_connection.send_pdu.call_args[0][0]
        assert sent_pdu.source_addr_ton == TonType.INTERNATIONAL
        assert sent_pdu.source_addr_npi == NpiType.ISDN
        assert sent_pdu.dest_addr_ton == TonType.NATIONAL
        assert sent_pdu.dest_addr_npi == NpiType.TELEX
        assert sent_pdu.service_type == 'SMS'
        assert sent_pdu.esm_class == 0x01
        assert sent_pdu.protocol_id == 0x02
        assert sent_pdu.priority_flag == 0x03
        assert sent_pdu.data_coding == DataCoding.UCS2


class TestSMPPServerStopWithExceptions:
    """Tests for server stop with client disconnect exceptions."""

    @pytest.mark.asyncio
    async def test_stop_with_client_disconnect_exception(self):
        """Test server stop when client disconnect raises exception."""
        server = SMPPServer()
        mock_server = AsyncMock()
        server._server = mock_server
        server._running = True

        # Add mock client that raises exception on disconnect
        mock_connection = AsyncMock()
        mock_connection.disconnect.side_effect = Exception('Disconnect failed')
        session = ClientSession(connection=mock_connection)
        server._clients = {'client1': session}

        # Should not raise exception
        await server.stop()

        assert server._running is False
        assert server._server is None
        assert server._clients == {}
        mock_connection.disconnect.assert_called_once()


class TestSMPPServerCustomAuthentication:
    """Tests for custom authentication."""

    def test_custom_authentication_success(self):
        """Test custom authentication that succeeds."""
        server = SMPPServer()

        def custom_auth(system_id, password, system_type):
            return system_id == 'valid_user' and password == 'valid_pass'

        server.authenticate = custom_auth

        result = server.authenticate('valid_user', 'valid_pass', 'test')
        assert result is True

        result = server.authenticate('invalid_user', 'invalid_pass', 'test')
        assert result is False

    def test_no_authentication(self):
        """Test when authentication is disabled."""
        server = SMPPServer()
        server.authenticate = None

        # Should always succeed when authenticate is None
        # This is tested in the bind request handling


class TestSMPPServerEdgeCases:
    """Tests for edge cases and error scenarios."""

    def test_client_count_after_operations(self):
        """Test client count after various operations."""
        server = SMPPServer()
        assert server.client_count == 0

        # Add clients
        server._clients = {'client1': Mock(), 'client2': Mock(), 'client3': Mock()}
        assert server.client_count == 3

        # Remove a client
        del server._clients['client2']
        assert server.client_count == 2

    def test_message_id_counter_overflow(self):
        """Test message ID counter behavior."""
        server = SMPPServer()
        server._message_id_counter = 999999999

        # Should continue incrementing
        msg_id = server._get_next_message_id()
        assert msg_id == '999999999'
        assert server._message_id_counter == 1000000000

    def test_get_bound_clients_mixed_states(self):
        """Test getting bound clients with mixed session states."""
        server = SMPPServer()

        bound_tx = Mock()
        bound_tx.bound = True

        bound_rx = Mock()
        bound_rx.bound = True

        unbound = Mock()
        unbound.bound = False

        not_bound_yet = Mock()
        not_bound_yet.bound = False

        server._clients = {
            'bound_tx': bound_tx,
            'bound_rx': bound_rx,
            'unbound': unbound,
            'not_bound_yet': not_bound_yet,
        }

        bound_clients = server.get_bound_clients()
        assert len(bound_clients) == 2
        assert bound_tx in bound_clients
        assert bound_rx in bound_clients
        assert unbound not in bound_clients
        assert not_bound_yet not in bound_clients

    @pytest.mark.asyncio
    async def test_handle_client_connection_no_peer_info(self):
        """Test client connection when peer info is not available."""
        server = SMPPServer()

        mock_reader = AsyncMock()
        mock_writer = AsyncMock()
        mock_writer.get_extra_info = Mock(return_value=None)  # No peer info

        mock_connection = AsyncMock(spec=SMPPConnection)

        with (
            patch('smpp.server.server.SMPPConnection', return_value=mock_connection),
            patch('asyncio.create_task'),
        ):
            await server._handle_client_connection(mock_reader, mock_writer)

            # Should still create connection with 'unknown' identifier
            assert 'unknown' in server._clients
