"""
Unit tests for SMPP Client implementation.

Tests all functionality of the SMPPClient class including connection management,
binding operations, message sending, event handling, and error scenarios.
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, Mock, patch, PropertyMock

from smpp.client.client import SMPPClient, BindType
from smpp.exceptions import (
    SMPPBindException,
    SMPPConnectionException,
    SMPPException,
    SMPPInvalidStateException,
    SMPPMessageException,
    SMPPTimeoutException,
)
from smpp.protocol import (
    BindTransmitter,
    CommandId,
    CommandStatus,
    DataCoding,
    DeliverSm,
    DeliverSmResp,
    EnquireLinkResp,
    NpiType,
    RegisteredDelivery,
    SubmitSm,
    TonType,
    UnbindResp,
)
from smpp.protocol.constants import DEFAULT_INTERFACE_VERSION
from smpp.transport import ConnectionState


class TestBindType:
    """Tests for BindType enum."""

    def test_bind_type_values(self):
        """Test BindType enum values."""
        assert BindType.TRANSMITTER.value == 'transmitter'
        assert BindType.RECEIVER.value == 'receiver'
        assert BindType.TRANSCEIVER.value == 'transceiver'


class TestSMPPClientInitialization:
    """Tests for SMPPClient initialization."""

    def test_init_default_values(self):
        """Test SMPPClient initialization with default values."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')

        assert client.host == 'localhost'
        assert client.port == 2775
        assert client.system_id == 'test_system'
        assert client.password == 'password'
        assert client.system_type == ''
        assert client.interface_version == DEFAULT_INTERFACE_VERSION
        assert client.addr_ton == TonType.UNKNOWN
        assert client.addr_npi == NpiType.UNKNOWN
        assert client.address_range == ''
        assert client.bind_timeout == 30.0
        assert client.response_timeout == 30.0

        assert not client.is_connected
        assert not client.is_bound
        assert client.bind_type is None
        assert client._bound is False
        assert client._bind_type is None

    def test_init_custom_values(self):
        """Test SMPPClient initialization with custom values."""
        client = SMPPClient(
            host='smpp.example.com',
            port=2776,
            system_id='custom_system',
            password='custom_pass',
            system_type='SMS_GATEWAY',
            interface_version=0x33,
            addr_ton=TonType.INTERNATIONAL,
            addr_npi=NpiType.ISDN,
            address_range='1234567890',
            bind_timeout=60.0,
            enquire_link_interval=120.0,
            response_timeout=45.0,
        )

        assert client.host == 'smpp.example.com'
        assert client.port == 2776
        assert client.system_id == 'custom_system'
        assert client.password == 'custom_pass'
        assert client.system_type == 'SMS_GATEWAY'
        assert client.interface_version == 0x33
        assert client.addr_ton == TonType.INTERNATIONAL
        assert client.addr_npi == NpiType.ISDN
        assert client.address_range == '1234567890'
        assert client.bind_timeout == 60.0
        assert client.response_timeout == 45.0

    @patch('smpp.client.client.SMPPConnection')
    def test_init_creates_connection(self, mock_connection_class):
        """Test that initialization creates SMPPConnection."""
        mock_connection = Mock()
        mock_connection_class.return_value = mock_connection

        client = SMPPClient('localhost', 2775, 'test_system', 'password')

        mock_connection_class.assert_called_once_with(
            host='localhost',
            port=2775,
            enquire_link_interval=60.0,
            read_timeout=30.0,
            write_timeout=30.0,
        )

        assert client._connection == mock_connection
        assert mock_connection.on_pdu_received == client._handle_pdu_received
        assert mock_connection.on_connection_lost == client._handle_connection_lost


class TestSMPPClientProperties:
    """Tests for SMPPClient properties."""

    def test_is_connected_true(self):
        """Test is_connected property when connected."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')
        client._connection = Mock()
        type(client._connection).is_connected = PropertyMock(return_value=True)

        assert client.is_connected is True

    def test_is_connected_false_no_connection(self):
        """Test is_connected property when no connection."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')
        client._connection = None

        assert client.is_connected is False

    def test_is_connected_false_not_connected(self):
        """Test is_connected property when connection exists but not connected."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')
        client._connection = Mock()
        client._connection.is_connected = False

        assert client.is_connected is False

    def test_is_bound_true(self):
        """Test is_bound property when bound and connected."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')
        client._connection = Mock()
        type(client._connection).is_connected = PropertyMock(return_value=True)
        client._bound = True

        assert client.is_bound is True

    def test_is_bound_false_not_bound(self):
        """Test is_bound property when not bound."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')
        client._connection = Mock()
        type(client._connection).is_connected = PropertyMock(return_value=True)
        client._bound = False

        assert client.is_bound is False

    def test_is_bound_false_not_connected(self):
        """Test is_bound property when bound but not connected."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')
        client._connection = Mock()
        client._connection.is_connected = False
        client._bound = True

        assert client.is_bound is False

    def test_bind_type_property(self):
        """Test bind_type property."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')

        assert client.bind_type is None

        client._bind_type = BindType.TRANSMITTER
        assert client.bind_type == BindType.TRANSMITTER

    def test_connection_state_property(self):
        """Test connection_state property."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')
        client._connection = Mock()
        client._connection.state = ConnectionState.OPEN

        assert client.connection_state == ConnectionState.OPEN

    def test_connection_state_property_no_connection(self):
        """Test connection_state property when no connection."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')
        client._connection = None

        assert client.connection_state == ConnectionState.CLOSED


class TestSMPPClientConnection:
    """Tests for SMPPClient connection management."""

    @pytest.mark.asyncio
    async def test_connect_success(self):
        """Test successful connection."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')
        client._connection = AsyncMock()
        client._connection.is_connected = False

        await client.connect()

        client._connection.connect.assert_called_once()

    @pytest.mark.asyncio
    async def test_connect_no_connection(self):
        """Test connect when no connection object."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')
        client._connection = None

        with pytest.raises(SMPPException, match='Connection not initialized'):
            await client.connect()

    @pytest.mark.asyncio
    async def test_connect_already_connected(self):
        """Test connect when already connected."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')
        client._connection = Mock()
        type(client._connection).is_connected = PropertyMock(return_value=True)

        with pytest.raises(SMPPConnectionException, match='Already connected'):
            await client.connect()

    @pytest.mark.asyncio
    async def test_disconnect_success(self):
        """Test successful disconnection."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')
        client._connection = AsyncMock()
        type(client._connection).is_connected = PropertyMock(return_value=True)
        client._bound = True
        client._bind_type = BindType.TRANSMITTER

        # Mock unbind method
        client.unbind = AsyncMock()

        await client.disconnect()

        client.unbind.assert_called_once()
        client._connection.disconnect.assert_called_once()
        assert client._bound is False
        assert client._bind_type is None

    @pytest.mark.asyncio
    async def test_disconnect_not_connected(self):
        """Test disconnect when not connected."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')
        client._connection = Mock()
        client._connection.is_connected = False

        await client.disconnect()

        # Should not call disconnect on connection

    @pytest.mark.asyncio
    async def test_disconnect_unbind_error(self):
        """Test disconnect when unbind fails."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')
        client._connection = AsyncMock()
        type(client._connection).is_connected = PropertyMock(return_value=True)
        client._bound = True

        # Mock unbind to raise exception
        client.unbind = AsyncMock(side_effect=Exception('Unbind failed'))

        await client.disconnect()

        # Should still call disconnect despite unbind error
        client._connection.disconnect.assert_called_once()
        assert client._bound is False
        assert client._bind_type is None


class TestSMPPClientBinding:
    """Tests for SMPPClient binding operations."""

    @pytest.mark.asyncio
    async def test_bind_transmitter_success(self):
        """Test successful bind as transmitter."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')
        client._connection = AsyncMock()
        type(client._connection).is_connected = PropertyMock(return_value=True)
        client._bound = False

        # Mock successful response
        response = Mock()
        response.command_status = CommandStatus.ESME_ROK
        client._connection.send_pdu.return_value = response

        # Mock set_bound_state as a regular method (not async)
        client._connection.set_bound_state = Mock()

        # Mock bind success handler
        client.on_bind_success = Mock()

        await client.bind_transmitter()

        assert client._bound is True
        assert client._bind_type == BindType.TRANSMITTER
        client._connection.set_bound_state.assert_called_once_with('transmitter')
        client.on_bind_success.assert_called_once_with(client, BindType.TRANSMITTER)

    @pytest.mark.asyncio
    async def test_bind_receiver_success(self):
        """Test successful bind as receiver."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')
        client._connection = AsyncMock()
        type(client._connection).is_connected = PropertyMock(return_value=True)
        client._bound = False

        # Mock successful response
        response = Mock()
        response.command_status = CommandStatus.ESME_ROK
        client._connection.send_pdu.return_value = response

        # Mock set_bound_state as a regular method (not async)
        client._connection.set_bound_state = Mock()

        await client.bind_receiver()

        assert client._bound is True
        assert client._bind_type == BindType.RECEIVER
        client._connection.set_bound_state.assert_called_once_with('receiver')

    @pytest.mark.asyncio
    async def test_bind_transceiver_success(self):
        """Test successful bind as transceiver."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')
        client._connection = AsyncMock()
        type(client._connection).is_connected = PropertyMock(return_value=True)
        client._bound = False

        # Mock successful response
        response = Mock()
        response.command_status = CommandStatus.ESME_ROK
        client._connection.send_pdu.return_value = response

        # Mock set_bound_state as a regular method (not async)
        client._connection.set_bound_state = Mock()

        await client.bind_transceiver()

        assert client._bound is True
        assert client._bind_type == BindType.TRANSCEIVER
        client._connection.set_bound_state.assert_called_once_with('transceiver')

    @pytest.mark.asyncio
    async def test_bind_not_connected(self):
        """Test bind when not connected."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')
        client._connection = Mock()
        client._connection.is_connected = False

        with pytest.raises(SMPPInvalidStateException, match='Not connected to SMSC'):
            await client.bind_transmitter()

    @pytest.mark.asyncio
    async def test_bind_already_bound(self):
        """Test bind when already bound."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')
        client._connection = Mock()
        type(client._connection).is_connected = PropertyMock(return_value=True)
        client._bound = True

        with pytest.raises(SMPPInvalidStateException, match='Already bound'):
            await client.bind_transmitter()

    @pytest.mark.asyncio
    async def test_bind_no_connection_object(self):
        """Test bind when connection object is None."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')
        client._connection = None

        with pytest.raises(SMPPInvalidStateException, match='Not connected to SMSC'):
            await client.bind_transmitter()

    @pytest.mark.asyncio
    async def test_bind_no_response(self):
        """Test bind when no response received."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')
        client._connection = AsyncMock()
        type(client._connection).is_connected = PropertyMock(return_value=True)
        client._bound = False
        client._connection.send_pdu.return_value = None

        with pytest.raises(SMPPBindException, match='No response received from server'):
            await client.bind_transmitter()

    @pytest.mark.asyncio
    async def test_bind_error_response(self):
        """Test bind when error response received."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')
        client._connection = AsyncMock()
        type(client._connection).is_connected = PropertyMock(return_value=True)
        client._bound = False

        # Mock error response
        response = Mock()
        response.command_status = CommandStatus.ESME_RINVPASWD
        client._connection.send_pdu.return_value = response

        with pytest.raises(SMPPBindException, match='Bind failed'):
            await client.bind_transmitter()

    @pytest.mark.asyncio
    async def test_bind_timeout(self):
        """Test bind timeout."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')
        client._connection = AsyncMock()
        type(client._connection).is_connected = PropertyMock(return_value=True)
        client._bound = False
        client._connection.send_pdu.side_effect = SMPPTimeoutException('Timeout')

        with pytest.raises(SMPPBindException, match='Bind timeout'):
            await client.bind_transmitter()

    @pytest.mark.asyncio
    async def test_bind_creates_correct_pdu(self):
        """Test that bind creates correct PDU with parameters."""
        client = SMPPClient(
            'localhost',
            2775,
            'test_system',
            'password',
            system_type='SMS_GW',
            interface_version=0x34,
            addr_ton=TonType.INTERNATIONAL,
            addr_npi=NpiType.ISDN,
            address_range='12345',
        )
        client._connection = AsyncMock()
        type(client._connection).is_connected = PropertyMock(return_value=True)
        client._bound = False

        # Mock successful response
        response = Mock()
        response.command_status = CommandStatus.ESME_ROK
        client._connection.send_pdu.return_value = response

        # Mock set_bound_state as a regular method (not async)
        client._connection.set_bound_state = Mock()

        await client.bind_transmitter()

        # Check that send_pdu was called with correct PDU
        call_args = client._connection.send_pdu.call_args[0]
        pdu = call_args[0]

        assert isinstance(pdu, BindTransmitter)
        assert pdu.system_id == 'test_system'
        assert pdu.password == 'password'
        assert pdu.system_type == 'SMS_GW'
        assert pdu.interface_version == 0x34
        assert pdu.addr_ton == TonType.INTERNATIONAL
        assert pdu.addr_npi == NpiType.ISDN
        assert pdu.address_range == '12345'

    @pytest.mark.asyncio
    async def test_bind_success_handler_exception(self):
        """Test bind success when handler raises exception."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')
        client._connection = AsyncMock()
        type(client._connection).is_connected = PropertyMock(return_value=True)
        client._bound = False

        # Mock successful response
        response = Mock()
        response.command_status = CommandStatus.ESME_ROK
        client._connection.send_pdu.return_value = response

        # Mock set_bound_state as a regular method (not async)
        client._connection.set_bound_state = Mock()

        # Mock bind success handler that raises exception
        client.on_bind_success = Mock(side_effect=Exception('Handler error'))

        # Should not raise exception from handler
        await client.bind_transmitter()

        assert client._bound is True
        assert client._bind_type == BindType.TRANSMITTER


class TestSMPPClientUnbinding:
    """Tests for SMPPClient unbinding operations."""

    @pytest.mark.asyncio
    async def test_unbind_success(self):
        """Test successful unbind."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')
        client._connection = AsyncMock()
        client._bound = True
        client._bind_type = BindType.TRANSMITTER

        # Mock successful response
        response = Mock()
        response.command_status = CommandStatus.ESME_ROK
        client._connection.send_pdu.return_value = response

        # Mock unbind handler
        client.on_unbind = Mock()

        await client.unbind()

        assert client._bound is False
        assert client._bind_type is None
        client.on_unbind.assert_called_once_with(client)

    @pytest.mark.asyncio
    async def test_unbind_not_bound(self):
        """Test unbind when not bound."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')
        client._bound = False

        with pytest.raises(SMPPInvalidStateException, match='Not bound'):
            await client.unbind()

    @pytest.mark.asyncio
    async def test_unbind_no_connection(self):
        """Test unbind when connection is None but client state thinks it's bound."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')
        # Create a mock connection first to make client "bound"
        client._connection = Mock()
        type(client._connection).is_connected = PropertyMock(return_value=True)
        client._bound = True
        client._bind_type = BindType.TRANSMITTER

        # Now set connection to None to simulate connection loss after binding
        client._connection = None

        # Should raise exception because is_bound will now return False
        with pytest.raises(SMPPInvalidStateException, match='Not bound'):
            await client.unbind()

    @pytest.mark.asyncio
    async def test_unbind_error_response(self):
        """Test unbind with error response."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')
        client._connection = AsyncMock()
        client._bound = True

        # Mock error response
        response = Mock()
        response.command_status = CommandStatus.ESME_RINVCMDID
        client._connection.send_pdu.return_value = response

        # Should not raise exception, just log warning
        await client.unbind()

        assert client._bound is False
        assert client._bind_type is None

    @pytest.mark.asyncio
    async def test_unbind_exception(self):
        """Test unbind when exception occurs."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')
        client._connection = AsyncMock()
        client._connection.send_pdu.side_effect = Exception('Send error')
        client._bound = True

        # Should not raise exception, just log warning
        await client.unbind()

        assert client._bound is False
        assert client._bind_type is None

    @pytest.mark.asyncio
    async def test_unbind_handler_exception(self):
        """Test unbind when handler raises exception."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')
        client._connection = AsyncMock()
        client._bound = True

        # Mock successful response
        response = Mock()
        response.command_status = CommandStatus.ESME_ROK
        client._connection.send_pdu.return_value = response

        # Mock unbind handler that raises exception
        client.on_unbind = Mock(side_effect=Exception('Handler error'))

        # Should not raise exception from handler
        await client.unbind()

        assert client._bound is False
        assert client._bind_type is None


class TestSMPPClientSubmitSm:
    """Tests for SMPPClient submit_sm operations."""

    @pytest.mark.asyncio
    async def test_submit_sm_success_transmitter(self):
        """Test successful submit_sm as transmitter."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')
        client._connection = AsyncMock()
        client._bound = True
        client._bind_type = BindType.TRANSMITTER

        # Mock successful response
        response = Mock()
        response.command_status = CommandStatus.ESME_ROK
        response.message_id = 'MSG123456'
        client._connection.send_pdu.return_value = response

        message_id = await client.submit_sm(
            source_addr='12345', destination_addr='67890', short_message='Test message'
        )

        assert message_id == 'MSG123456'

    @pytest.mark.asyncio
    async def test_submit_sm_success_transceiver(self):
        """Test successful submit_sm as transceiver."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')
        client._connection = AsyncMock()
        client._bound = True
        client._bind_type = BindType.TRANSCEIVER

        # Mock successful response
        response = Mock()
        response.command_status = CommandStatus.ESME_ROK
        response.message_id = 'MSG789012'
        client._connection.send_pdu.return_value = response

        message_id = await client.submit_sm(
            source_addr='12345', destination_addr='67890', short_message='Test message'
        )

        assert message_id == 'MSG789012'

    @pytest.mark.asyncio
    async def test_submit_sm_not_bound(self):
        """Test submit_sm when not bound."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')
        client._bound = False

        with pytest.raises(SMPPInvalidStateException, match='Not bound to SMSC'):
            await client.submit_sm('12345', '67890', 'Test message')

    @pytest.mark.asyncio
    async def test_submit_sm_receiver_bind(self):
        """Test submit_sm with receiver bind type."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')
        client._connection = Mock()
        type(client._connection).is_connected = PropertyMock(return_value=True)
        client._bound = True
        client._bind_type = BindType.RECEIVER

        with pytest.raises(
            SMPPInvalidStateException, match='Cannot send SMS with bind type receiver'
        ):
            await client.submit_sm('12345', '67890', 'Test message')

    @pytest.mark.asyncio
    async def test_submit_sm_no_bind_type(self):
        """Test submit_sm with no bind type."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')
        client._connection = Mock()
        type(client._connection).is_connected = PropertyMock(return_value=True)
        client._bound = True
        client._bind_type = None

        with pytest.raises(
            SMPPInvalidStateException, match='Cannot send SMS with bind type unknown'
        ):
            await client.submit_sm('12345', '67890', 'Test message')

    @pytest.mark.asyncio
    async def test_submit_sm_message_too_long(self):
        """Test submit_sm with message too long."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')
        client._connection = Mock()
        type(client._connection).is_connected = PropertyMock(return_value=True)
        client._bound = True
        client._bind_type = BindType.TRANSMITTER

        long_message = 'a' * 256  # > 255 bytes

        with pytest.raises(SMPPMessageException, match='Message too long'):
            await client.submit_sm('12345', '67890', long_message)

    @pytest.mark.asyncio
    async def test_submit_sm_no_connection(self):
        """Test submit_sm when connection is None after being bound."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')
        # First establish that client is bound
        client._connection = Mock()
        type(client._connection).is_connected = PropertyMock(return_value=True)
        client._bound = True
        client._bind_type = BindType.TRANSMITTER

        # Then set connection to None to simulate connection loss
        client._connection = None

        # Should now fail at the is_bound check because connection is None
        with pytest.raises(SMPPInvalidStateException, match='Not bound to SMSC'):
            await client.submit_sm('12345', '67890', 'Test message')

    @pytest.mark.asyncio
    async def test_submit_sm_no_response(self):
        """Test submit_sm when no response received."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')
        client._connection = AsyncMock()
        client._bound = True
        client._bind_type = BindType.TRANSMITTER
        client._connection.send_pdu.return_value = None

        with pytest.raises(
            SMPPMessageException, match='No response received from SMSC'
        ):
            await client.submit_sm('12345', '67890', 'Test message')

    @pytest.mark.asyncio
    async def test_submit_sm_error_response(self):
        """Test submit_sm when error response received."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')
        client._connection = AsyncMock()
        client._bound = True
        client._bind_type = BindType.TRANSMITTER

        # Mock error response
        response = Mock()
        response.command_status = CommandStatus.ESME_RINVDESTADR
        client._connection.send_pdu.return_value = response

        with pytest.raises(SMPPMessageException, match='Message submission failed'):
            await client.submit_sm('12345', '67890', 'Test message')

    @pytest.mark.asyncio
    async def test_submit_sm_timeout(self):
        """Test submit_sm timeout."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')
        client._connection = AsyncMock()
        client._bound = True
        client._bind_type = BindType.TRANSMITTER
        client._connection.send_pdu.side_effect = SMPPTimeoutException('Timeout')

        with pytest.raises(SMPPMessageException, match='Message submission timeout'):
            await client.submit_sm('12345', '67890', 'Test message')

    @pytest.mark.asyncio
    async def test_submit_sm_with_all_parameters(self):
        """Test submit_sm with all parameters."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')
        client._connection = AsyncMock()
        client._bound = True
        client._bind_type = BindType.TRANSMITTER

        # Mock successful response
        response = Mock()
        response.command_status = CommandStatus.ESME_ROK
        response.message_id = 'MSG123456'
        client._connection.send_pdu.return_value = response

        message_id = await client.submit_sm(
            source_addr='12345',
            destination_addr='67890',
            short_message='Test message',
            source_addr_ton=TonType.INTERNATIONAL,
            source_addr_npi=NpiType.ISDN,
            dest_addr_ton=TonType.NATIONAL,
            dest_addr_npi=NpiType.TELEX,
            service_type='SMS',
            esm_class=1,
            protocol_id=2,
            priority_flag=3,
            schedule_delivery_time='240101120000000+',
            validity_period='240101120000000+',
            registered_delivery=RegisteredDelivery.SUCCESS_FAILURE,
            replace_if_present_flag=1,
            data_coding=DataCoding.LATIN_1,
            sm_default_msg_id=5,
            timeout=60.0,
        )

        assert message_id == 'MSG123456'

        # Check that send_pdu was called with correct PDU
        call_args = client._connection.send_pdu.call_args[0]
        pdu = call_args[0]

        assert isinstance(pdu, SubmitSm)
        assert pdu.source_addr == '12345'
        assert pdu.destination_addr == '67890'
        assert pdu.short_message == b'Test message'
        assert pdu.source_addr_ton == TonType.INTERNATIONAL
        assert pdu.source_addr_npi == NpiType.ISDN
        assert pdu.dest_addr_ton == TonType.NATIONAL
        assert pdu.dest_addr_npi == NpiType.TELEX
        assert pdu.service_type == 'SMS'
        assert pdu.esm_class == 1
        assert pdu.protocol_id == 2
        assert pdu.priority_flag == 3
        assert pdu.registered_delivery == RegisteredDelivery.SUCCESS_FAILURE
        assert pdu.data_coding == DataCoding.LATIN_1

    @pytest.mark.asyncio
    async def test_submit_sm_null_message_id(self):
        """Test submit_sm when message_id is None."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')
        client._connection = AsyncMock()
        client._bound = True
        client._bind_type = BindType.TRANSMITTER

        # Mock successful response with None message_id
        response = Mock()
        response.command_status = CommandStatus.ESME_ROK
        response.message_id = None
        client._connection.send_pdu.return_value = response

        message_id = await client.submit_sm('12345', '67890', 'Test message')

        assert message_id == ''


class TestSMPPClientEnquireLink:
    """Tests for SMPPClient enquire_link operations."""

    @pytest.mark.asyncio
    async def test_enquire_link_success(self):
        """Test successful enquire_link."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')
        client._connection = AsyncMock()
        type(client._connection).is_connected = PropertyMock(return_value=True)

        # Mock successful response
        response = Mock()
        response.command_status = CommandStatus.ESME_ROK
        client._connection.send_pdu.return_value = response

        result = await client.enquire_link()

        assert result is True

    @pytest.mark.asyncio
    async def test_enquire_link_not_connected(self):
        """Test enquire_link when not connected."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')
        client._connection = Mock()
        client._connection.is_connected = False

        with pytest.raises(SMPPInvalidStateException, match='Not connected to SMSC'):
            await client.enquire_link()

    @pytest.mark.asyncio
    async def test_enquire_link_no_connection(self):
        """Test enquire_link when connection is None."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')
        client._connection = None

        with pytest.raises(SMPPInvalidStateException, match='Not connected to SMSC'):
            await client.enquire_link()

    @pytest.mark.asyncio
    async def test_enquire_link_no_response(self):
        """Test enquire_link when no response received."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')
        client._connection = AsyncMock()
        type(client._connection).is_connected = PropertyMock(return_value=True)
        client._connection.send_pdu.return_value = None

        result = await client.enquire_link()

        assert result is False

    @pytest.mark.asyncio
    async def test_enquire_link_error_response(self):
        """Test enquire_link when error response received."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')
        client._connection = AsyncMock()
        type(client._connection).is_connected = PropertyMock(return_value=True)

        # Mock error response
        response = Mock()
        response.command_status = CommandStatus.ESME_RINVCMDID
        client._connection.send_pdu.return_value = response

        result = await client.enquire_link()

        assert result is False

    @pytest.mark.asyncio
    async def test_enquire_link_exception(self):
        """Test enquire_link when exception occurs."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')
        client._connection = AsyncMock()
        type(client._connection).is_connected = PropertyMock(return_value=True)
        client._connection.send_pdu.side_effect = Exception('Send error')

        result = await client.enquire_link()

        assert result is False

    @pytest.mark.asyncio
    async def test_enquire_link_custom_timeout(self):
        """Test enquire_link with custom timeout."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')
        client._connection = AsyncMock()
        type(client._connection).is_connected = PropertyMock(return_value=True)

        # Mock successful response
        response = Mock()
        response.command_status = CommandStatus.ESME_ROK
        client._connection.send_pdu.return_value = response

        result = await client.enquire_link(timeout=60.0)

        assert result is True

        # Check timeout was passed to send_pdu
        call_kwargs = client._connection.send_pdu.call_args[1]
        assert call_kwargs['timeout'] == 60.0


class TestSMPPClientPDUHandling:
    """Tests for SMPPClient PDU handling."""

    def test_handle_pdu_received_deliver_sm(self):
        """Test handling deliver_sm PDU."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')
        client._handle_deliver_sm = Mock()

        deliver_pdu = Mock(spec=DeliverSm)

        client._handle_pdu_received(deliver_pdu)

        client._handle_deliver_sm.assert_called_once_with(deliver_pdu)

    @patch('asyncio.create_task')
    def test_handle_pdu_received_enquire_link(self, mock_create_task):
        """Test handling enquire_link PDU."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')

        enquire_pdu = Mock()
        enquire_pdu.command_id = CommandId.ENQUIRE_LINK
        enquire_pdu.sequence_number = 12345

        client._handle_pdu_received(enquire_pdu)

        mock_create_task.assert_called_once()
        # Check that the coroutine is for sending enquire_link_resp
        coroutine = mock_create_task.call_args[0][0]
        assert coroutine.cr_frame.f_code.co_name == '_send_enquire_link_resp'

    @patch('asyncio.create_task')
    def test_handle_pdu_received_unbind(self, mock_create_task):
        """Test handling unbind PDU."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')

        unbind_pdu = Mock()
        unbind_pdu.command_id = CommandId.UNBIND
        unbind_pdu.sequence_number = 54321

        client._handle_pdu_received(unbind_pdu)

        mock_create_task.assert_called_once()
        # Check that the coroutine is for handling unbind request
        coroutine = mock_create_task.call_args[0][0]
        assert coroutine.cr_frame.f_code.co_name == '_handle_unbind_request'

    def test_handle_pdu_received_unhandled(self):
        """Test handling unhandled PDU."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')

        unknown_pdu = Mock()
        unknown_pdu.command_id = CommandId.ALERT_NOTIFICATION
        unknown_pdu.__class__.__name__ = 'AlertNotification'

        # Should not raise exception
        client._handle_pdu_received(unknown_pdu)

    def test_handle_pdu_received_exception(self):
        """Test handling PDU when exception occurs."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')
        client._handle_deliver_sm = Mock(side_effect=Exception('Handler error'))

        deliver_pdu = Mock(spec=DeliverSm)

        # Should not raise exception
        client._handle_pdu_received(deliver_pdu)

    @patch('asyncio.create_task')
    def test_handle_deliver_sm(self, mock_create_task):
        """Test handling deliver_sm."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')
        client.on_deliver_sm = Mock()

        # Mock the connection to avoid coroutine warnings
        client._connection = AsyncMock()

        # Make the create_task mock close the coroutine to avoid warnings
        def close_coroutine(coro):
            coro.close()
            return Mock()

        mock_create_task.side_effect = close_coroutine

        deliver_pdu = Mock()
        deliver_pdu.sequence_number = 12345
        deliver_pdu.source_addr = '12345'
        deliver_pdu.destination_addr = '67890'

        client._handle_deliver_sm(deliver_pdu)

        # Should create task for sending response
        mock_create_task.assert_called_once()

        # Should call handler
        client.on_deliver_sm.assert_called_once_with(client, deliver_pdu)

    @patch('asyncio.create_task')
    def test_handle_deliver_sm_handler_exception(self, mock_create_task):
        """Test handling deliver_sm when handler raises exception."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')
        client.on_deliver_sm = Mock(side_effect=Exception('Handler error'))

        # Mock the connection to avoid coroutine warnings
        client._connection = AsyncMock()

        # Make the create_task mock close the coroutine to avoid warnings
        def close_coroutine(coro):
            coro.close()
            return Mock()

        mock_create_task.side_effect = close_coroutine

        deliver_pdu = Mock()
        deliver_pdu.sequence_number = 12345
        deliver_pdu.source_addr = '12345'
        deliver_pdu.destination_addr = '67890'

        # Should not raise exception
        client._handle_deliver_sm(deliver_pdu)

    @pytest.mark.asyncio
    async def test_send_deliver_sm_resp(self):
        """Test sending deliver_sm_resp."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')
        client._connection = AsyncMock()

        await client._send_deliver_sm_resp(12345)

        # Check that send_pdu was called with correct PDU
        call_args = client._connection.send_pdu.call_args[0]
        pdu = call_args[0]

        assert isinstance(pdu, DeliverSmResp)
        assert pdu.sequence_number == 12345

        call_kwargs = client._connection.send_pdu.call_args[1]
        assert call_kwargs['wait_response'] is False

    @pytest.mark.asyncio
    async def test_send_deliver_sm_resp_exception(self):
        """Test sending deliver_sm_resp when exception occurs."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')
        client._connection = AsyncMock()
        client._connection.send_pdu.side_effect = Exception('Send error')

        # Should not raise exception
        await client._send_deliver_sm_resp(12345)

    @pytest.mark.asyncio
    async def test_send_enquire_link_resp(self):
        """Test sending enquire_link_resp."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')
        client._connection = AsyncMock()

        await client._send_enquire_link_resp(54321)

        # Check that send_pdu was called with correct PDU
        call_args = client._connection.send_pdu.call_args[0]
        pdu = call_args[0]

        assert isinstance(pdu, EnquireLinkResp)
        assert pdu.sequence_number == 54321

        call_kwargs = client._connection.send_pdu.call_args[1]
        assert call_kwargs['wait_response'] is False

    @pytest.mark.asyncio
    async def test_send_enquire_link_resp_exception(self):
        """Test sending enquire_link_resp when exception occurs."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')
        client._connection = AsyncMock()
        client._connection.send_pdu.side_effect = Exception('Send error')

        # Should not raise exception
        await client._send_enquire_link_resp(54321)

    @pytest.mark.asyncio
    async def test_handle_unbind_request(self):
        """Test handling unbind request."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')
        client._connection = AsyncMock()
        client._bound = True
        client._bind_type = BindType.TRANSMITTER
        client.on_unbind = Mock()

        await client._handle_unbind_request(99999)

        # Check that send_pdu was called with correct PDU
        call_args = client._connection.send_pdu.call_args[0]
        pdu = call_args[0]

        assert isinstance(pdu, UnbindResp)
        assert pdu.sequence_number == 99999

        # Check state was updated
        assert client._bound is False
        assert client._bind_type is None

        # Check handler was called
        client.on_unbind.assert_called_once_with(client)

    @pytest.mark.asyncio
    async def test_handle_unbind_request_exception(self):
        """Test handling unbind request when exception occurs."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')
        client._connection = AsyncMock()
        client._connection.send_pdu.side_effect = Exception('Send error')
        client._bound = True

        # Should not raise exception
        await client._handle_unbind_request(99999)

    @pytest.mark.asyncio
    async def test_handle_unbind_request_handler_exception(self):
        """Test handling unbind request when handler raises exception."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')
        client._connection = AsyncMock()
        client._bound = True
        client.on_unbind = Mock(side_effect=Exception('Handler error'))

        # Should not raise exception
        await client._handle_unbind_request(99999)

        # State should still be updated
        assert client._bound is False


class TestSMPPClientConnectionLost:
    """Tests for SMPPClient connection lost handling."""

    def test_handle_connection_lost(self):
        """Test handling connection lost."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')
        client._bound = True
        client._bind_type = BindType.TRANSMITTER
        client.on_connection_lost = Mock()

        error = Exception('Connection lost')
        client._handle_connection_lost(error)

        assert client._bound is False
        assert client._bind_type is None
        client.on_connection_lost.assert_called_once_with(client, error)

    def test_handle_connection_lost_handler_exception(self):
        """Test handling connection lost when handler raises exception."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')
        client._bound = True
        client.on_connection_lost = Mock(side_effect=Exception('Handler error'))

        error = Exception('Connection lost')

        # Should not raise exception
        client._handle_connection_lost(error)

        # State should still be updated
        assert client._bound is False


class TestSMPPClientContextManager:
    """Tests for SMPPClient context manager."""

    @pytest.mark.asyncio
    async def test_context_manager_success(self):
        """Test successful context manager usage."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')
        client.connect = AsyncMock()
        client.disconnect = AsyncMock()

        async with client as c:
            assert c is client
            client.connect.assert_called_once()

        client.disconnect.assert_called_once()

    @pytest.mark.asyncio
    async def test_context_manager_exception(self):
        """Test context manager when exception occurs."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')
        client.connect = AsyncMock()
        client.disconnect = AsyncMock()

        with pytest.raises(ValueError):
            async with client:
                client.connect.assert_called_once()
                raise ValueError('Test error')

        client.disconnect.assert_called_once()


class TestSMPPClientWaitMethods:
    """Tests for SMPPClient wait methods."""

    @pytest.mark.asyncio
    async def test_wait_for_connection_success(self):
        """Test wait_for_connection when connection succeeds."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')
        client._connection = Mock()

        # Simulate connection after delay
        async def set_connected():
            await asyncio.sleep(0.2)
            type(client._connection).is_connected = PropertyMock(return_value=True)

        client._connection.is_connected = False
        asyncio.create_task(set_connected())

        result = await client.wait_for_connection(timeout=1.0)

        assert result is True
        assert client.is_connected is True

    @pytest.mark.asyncio
    async def test_wait_for_connection_timeout(self):
        """Test wait_for_connection timeout."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')
        client._connection = Mock()
        client._connection.is_connected = False

        result = await client.wait_for_connection(timeout=0.1)

        assert result is False

    @pytest.mark.asyncio
    async def test_wait_for_connection_already_connected(self):
        """Test wait_for_connection when already connected."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')
        client._connection = Mock()
        type(client._connection).is_connected = PropertyMock(return_value=True)

        result = await client.wait_for_connection(timeout=1.0)

        assert result is True

    @pytest.mark.asyncio
    async def test_wait_for_bind_success(self):
        """Test wait_for_bind when bind succeeds."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')
        client._connection = Mock()
        type(client._connection).is_connected = PropertyMock(return_value=True)

        # Simulate bind after delay
        async def set_bound():
            await asyncio.sleep(0.2)
            client._bound = True

        client._bound = False
        asyncio.create_task(set_bound())

        result = await client.wait_for_bind(timeout=1.0)

        assert result is True
        assert client.is_bound is True

    @pytest.mark.asyncio
    async def test_wait_for_bind_timeout(self):
        """Test wait_for_bind timeout."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')
        client._connection = Mock()
        type(client._connection).is_connected = PropertyMock(return_value=True)
        client._bound = False

        result = await client.wait_for_bind(timeout=0.1)

        assert result is False

    @pytest.mark.asyncio
    async def test_wait_for_bind_already_bound(self):
        """Test wait_for_bind when already bound."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')
        client._connection = Mock()
        type(client._connection).is_connected = PropertyMock(return_value=True)
        client._bound = True

        result = await client.wait_for_bind(timeout=1.0)

        assert result is True


class TestSMPPClientRepr:
    """Tests for SMPPClient string representation."""

    def test_repr(self):
        """Test string representation."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')
        client._bound = False

        result = repr(client)

        expected = (
            'SMPPClient(host=localhost, port=2775, system_id=test_system, bound=False)'
        )
        assert result == expected

    def test_repr_bound(self):
        """Test string representation when bound."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')
        client._connection = Mock()
        type(client._connection).is_connected = PropertyMock(return_value=True)
        client._bound = True

        result = repr(client)

        expected = (
            'SMPPClient(host=localhost, port=2775, system_id=test_system, bound=True)'
        )
        assert result == expected


class TestSMPPClientEventHandlers:
    """Tests for SMPPClient event handlers."""

    def test_event_handlers_initialization(self):
        """Test that event handlers are initialized to None."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')

        assert client.on_deliver_sm is None
        assert client.on_connection_lost is None
        assert client.on_bind_success is None
        assert client.on_unbind is None

    def test_set_event_handlers(self):
        """Test setting event handlers."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')

        def deliver_handler(client, pdu):
            pass

        def connection_lost_handler(client, error):
            pass

        def bind_success_handler(client, bind_type):
            pass

        def unbind_handler(client):
            pass

        client.on_deliver_sm = deliver_handler
        client.on_connection_lost = connection_lost_handler
        client.on_bind_success = bind_success_handler
        client.on_unbind = unbind_handler

        assert client.on_deliver_sm == deliver_handler
        assert client.on_connection_lost == connection_lost_handler
        assert client.on_bind_success == bind_success_handler
        assert client.on_unbind == unbind_handler


class TestSMPPClientEdgeCases:
    """Tests for edge cases and boundary conditions."""

    @pytest.mark.asyncio
    async def test_submit_sm_unicode_message(self):
        """Test submit_sm with Unicode message."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')
        client._connection = AsyncMock()
        client._bound = True
        client._bind_type = BindType.TRANSMITTER

        # Mock successful response
        response = Mock()
        response.command_status = CommandStatus.ESME_ROK
        response.message_id = 'MSG123456'
        client._connection.send_pdu.return_value = response

        # Unicode message
        unicode_message = 'Hello 🌍'

        message_id = await client.submit_sm('12345', '67890', unicode_message)

        assert message_id == 'MSG123456'

        # Check that message was encoded correctly
        call_args = client._connection.send_pdu.call_args[0]
        pdu = call_args[0]
        assert pdu.short_message == unicode_message.encode('utf-8')

    @pytest.mark.asyncio
    async def test_submit_sm_boundary_message_length(self):
        """Test submit_sm with message at boundary length."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')
        client._connection = AsyncMock()
        client._bound = True
        client._bind_type = BindType.TRANSMITTER

        # Mock successful response
        response = Mock()
        response.command_status = CommandStatus.ESME_ROK
        response.message_id = 'MSG123456'
        client._connection.send_pdu.return_value = response

        # Message with exactly 255 bytes
        boundary_message = 'a' * 255

        message_id = await client.submit_sm('12345', '67890', boundary_message)

        assert message_id == 'MSG123456'

    def test_connection_state_transitions(self):
        """Test connection state property during state transitions."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')

        # Initially closed
        client._connection = None
        assert client.connection_state == ConnectionState.CLOSED

        # Connected
        client._connection = Mock()
        client._connection.state = ConnectionState.OPEN
        assert client.connection_state == ConnectionState.OPEN

        # Bound
        client._connection.state = ConnectionState.BOUND_TX
        assert client.connection_state == ConnectionState.BOUND_TX

    @pytest.mark.asyncio
    async def test_multiple_binds_sequence(self):
        """Test binding sequence (bind, unbind, rebind)."""
        client = SMPPClient('localhost', 2775, 'test_system', 'password')
        client._connection = AsyncMock()
        type(client._connection).is_connected = PropertyMock(return_value=True)

        # Mock successful responses
        response = Mock()
        response.command_status = CommandStatus.ESME_ROK
        client._connection.send_pdu.return_value = response

        # Mock set_bound_state as a regular method (not async)
        client._connection.set_bound_state = Mock()

        # First bind
        await client.bind_transmitter()
        assert client.is_bound is True
        assert client.bind_type == BindType.TRANSMITTER

        # Unbind
        await client.unbind()
        assert client.is_bound is False
        assert client.bind_type is None

        # Rebind as different type
        await client.bind_receiver()
        assert client.is_bound is True
        assert client.bind_type == BindType.RECEIVER
