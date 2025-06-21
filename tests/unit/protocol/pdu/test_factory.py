"""Unit tests for SMPP PDU factory."""

import pytest

from smpp.exceptions import SMPPPDUException
from smpp.protocol.constants import CommandId, CommandStatus
from smpp.protocol.pdu.base import PDU
from smpp.protocol.pdu.bind import BindTransmitter, BindTransmitterResp
from smpp.protocol.pdu.message import SubmitSm, SubmitSmResp
from smpp.protocol.pdu.session import EnquireLink, EnquireLinkResp, GenericNack
from smpp.protocol.pdu.factory import (
    PDU_CLASSES,
    get_pdu_class,
    create_pdu,
    create_typed_pdu,
    create_request_pdu,
    create_response_pdu,
    create_error_response,
    decode_pdu,
    is_command_supported,
    get_pdu_name,
    create_bind_pdu,
    create_submit_sm_pdu,
    create_enquire_link_pdu,
    create_generic_nack_pdu,
)


class TestPDUClasses:
    """Test PDU_CLASSES mapping."""

    def test_bind_commands(self):
        """Test bind command mappings."""
        assert PDU_CLASSES[CommandId.BIND_TRANSMITTER] == BindTransmitter
        assert PDU_CLASSES[CommandId.BIND_TRANSMITTER_RESP] == BindTransmitterResp

    def test_message_commands(self):
        """Test message command mappings."""
        assert PDU_CLASSES[CommandId.SUBMIT_SM] == SubmitSm
        assert PDU_CLASSES[CommandId.SUBMIT_SM_RESP] == SubmitSmResp

    def test_session_commands(self):
        """Test session command mappings."""
        assert PDU_CLASSES[CommandId.ENQUIRE_LINK] == EnquireLink
        assert PDU_CLASSES[CommandId.ENQUIRE_LINK_RESP] == EnquireLinkResp
        assert PDU_CLASSES[CommandId.GENERIC_NACK] == GenericNack

    def test_all_commands_have_classes(self):
        """Test that all mapped commands have valid classes."""
        for command_id, pdu_class in PDU_CLASSES.items():
            assert issubclass(pdu_class, PDU)
            assert command_id is not None


class TestGetPDUClass:
    """Test get_pdu_class function."""

    def test_valid_command_id(self):
        """Test getting PDU class for valid command ID."""
        pdu_class = get_pdu_class(CommandId.BIND_TRANSMITTER)
        assert pdu_class == BindTransmitter

    def test_invalid_command_id(self):
        """Test getting PDU class for invalid command ID."""
        with pytest.raises(SMPPPDUException):
            get_pdu_class(0x12345678)

    def test_zero_command_id(self):
        """Test getting PDU class for zero command ID."""
        with pytest.raises(SMPPPDUException):
            get_pdu_class(0)


class TestCreatePDU:
    """Test create_pdu function."""

    def test_create_bind_transmitter(self):
        """Test creating BindTransmitter PDU."""
        pdu = create_pdu(CommandId.BIND_TRANSMITTER, system_id='test')
        assert isinstance(pdu, BindTransmitter)
        assert pdu.command_id == CommandId.BIND_TRANSMITTER
        assert pdu.system_id == 'test'

    def test_create_submit_sm(self):
        """Test creating SubmitSm PDU."""
        pdu = create_pdu(
            CommandId.SUBMIT_SM,
            source_addr='12345',
            destination_addr='67890',
            short_message=b'Hello',
        )
        assert isinstance(pdu, SubmitSm)
        assert pdu.command_id == CommandId.SUBMIT_SM
        assert pdu.source_addr == '12345'
        assert pdu.destination_addr == '67890'
        assert pdu.short_message == b'Hello'

    def test_create_enquire_link(self):
        """Test creating EnquireLink PDU."""
        pdu = create_pdu(CommandId.ENQUIRE_LINK, sequence_number=42)
        assert isinstance(pdu, EnquireLink)
        assert pdu.command_id == CommandId.ENQUIRE_LINK
        assert pdu.sequence_number == 42

    def test_create_invalid_command_id(self):
        """Test creating PDU with invalid command ID."""
        with pytest.raises(SMPPPDUException):
            create_pdu(0x99999999)

    def test_create_with_invalid_params(self):
        """Test creating PDU with invalid parameters."""
        with pytest.raises(SMPPPDUException):
            create_pdu(CommandId.BIND_TRANSMITTER, invalid_param='value')


class TestCreateTypedPDU:
    """Test create_typed_pdu function."""

    def test_create_typed_pdu_success(self):
        """Test creating typed PDU successfully."""
        pdu = create_typed_pdu(
            BindTransmitter, CommandId.BIND_TRANSMITTER, system_id='test'
        )
        assert isinstance(pdu, BindTransmitter)
        assert pdu.system_id == 'test'

    def test_create_typed_pdu_type_mismatch(self):
        """Test creating typed PDU with type mismatch."""
        with pytest.raises(SMPPPDUException):
            create_typed_pdu(
                BindTransmitter,
                CommandId.SUBMIT_SM,  # Wrong command ID
                system_id='test',
            )

    def test_create_typed_pdu_invalid_command(self):
        """Test creating typed PDU with invalid command ID."""
        with pytest.raises(SMPPPDUException):
            create_typed_pdu(BindTransmitter, 0x99999999)


class TestCreateRequestPDU:
    """Test create_request_pdu function."""

    def test_create_request_pdu_success(self):
        """Test creating request PDU successfully."""
        pdu = create_request_pdu(CommandId.BIND_TRANSMITTER, system_id='test')
        assert isinstance(pdu, BindTransmitter)
        assert pdu.system_id == 'test'

    def test_create_request_pdu_with_response_id(self):
        """Test creating request PDU with response command ID."""
        with pytest.raises(SMPPPDUException, match='is a response, not a request'):
            create_request_pdu(CommandId.BIND_TRANSMITTER_RESP)

    def test_create_request_pdu_invalid_command(self):
        """Test creating request PDU with invalid command ID."""
        with pytest.raises(SMPPPDUException):
            create_request_pdu(0x12345678)


class TestCreateResponsePDU:
    """Test create_response_pdu function."""

    def test_create_response_pdu_success(self):
        """Test creating response PDU successfully."""
        pdu = create_response_pdu(
            CommandId.BIND_TRANSMITTER,
            sequence_number=42,
            command_status=CommandStatus.ESME_ROK,
            system_id='smsc',
        )
        assert isinstance(pdu, BindTransmitterResp)
        assert pdu.command_id == CommandId.BIND_TRANSMITTER_RESP
        assert pdu.sequence_number == 42
        assert pdu.command_status == CommandStatus.ESME_ROK
        assert pdu.system_id == 'smsc'

    def test_create_response_pdu_default_status(self):
        """Test creating response PDU with default status."""
        pdu = create_response_pdu(
            CommandId.SUBMIT_SM, sequence_number=123, message_id='MSG123'
        )
        assert isinstance(pdu, SubmitSmResp)
        assert pdu.command_status == 0  # Default
        assert pdu.sequence_number == 123
        assert pdu.message_id == 'MSG123'

    def test_create_response_pdu_from_response_id(self):
        """Test creating response PDU from response command ID."""
        with pytest.raises(SMPPPDUException, match='is already a response'):
            create_response_pdu(CommandId.BIND_TRANSMITTER_RESP, 42)

    def test_create_response_pdu_invalid_command(self):
        """Test creating response PDU for invalid command."""
        with pytest.raises(SMPPPDUException):
            create_response_pdu(0x12345678, 42)


class TestCreateErrorResponse:
    """Test create_error_response function."""

    def test_create_error_response_basic(self):
        """Test creating basic error response."""
        request = BindTransmitter(sequence_number=42, system_id='test')
        error_response = create_error_response(request, CommandStatus.ESME_RBINDFAIL)

        assert isinstance(error_response, BindTransmitterResp)
        assert error_response.sequence_number == 42
        assert error_response.command_status == CommandStatus.ESME_RBINDFAIL

    def test_create_error_response_with_message(self):
        """Test creating error response with message."""
        request = SubmitSm(sequence_number=123, short_message=b'test')
        error_msg = 'Message too long'
        error_response = create_error_response(
            request, CommandStatus.ESME_RINVMSGLEN, error_msg
        )

        assert isinstance(error_response, SubmitSmResp)
        assert error_response.sequence_number == 123
        assert error_response.command_status == CommandStatus.ESME_RINVMSGLEN

        # Check that error message was added as optional parameter
        assert len(error_response.optional_parameters) == 1
        assert error_response.optional_parameters[0].tag == 0x001D
        assert error_response.optional_parameters[0].value == error_msg.encode('utf-8')

    def test_create_error_response_for_response_pdu(self):
        """Test creating error response for response PDU."""
        response_pdu = BindTransmitterResp(sequence_number=42)
        with pytest.raises(
            SMPPPDUException, match='Cannot create error response for response PDU'
        ):
            create_error_response(response_pdu, CommandStatus.ESME_RINVCMDID)

    def test_create_error_response_unknown_request(self):
        """Test creating error response for unknown request type."""

        # Create a mock PDU with unknown command ID
        class UnknownPDU(PDU):
            def encode_body(self):
                return b''

            def decode_body(self, data, offset=0):
                return offset

        unknown_pdu = UnknownPDU(command_id=0x99999999, sequence_number=42)
        with pytest.raises(
            SMPPPDUException, match='Cannot create error response for response PDU'
        ):
            create_error_response(unknown_pdu, CommandStatus.ESME_RINVCMDID)


class TestCommandUtilities:
    """Test command utility functions."""

    def test_is_command_supported(self):
        """Test is_command_supported function."""
        assert is_command_supported(CommandId.BIND_TRANSMITTER) is True
        assert is_command_supported(CommandId.SUBMIT_SM) is True
        assert is_command_supported(CommandId.ENQUIRE_LINK) is True
        assert is_command_supported(0x99999999) is False

    def test_get_pdu_name(self):
        """Test get_pdu_name function."""
        assert get_pdu_name(CommandId.BIND_TRANSMITTER) == 'BindTransmitter'
        assert get_pdu_name(CommandId.SUBMIT_SM) == 'SubmitSm'
        assert get_pdu_name(CommandId.ENQUIRE_LINK) == 'EnquireLink'

    def test_get_pdu_name_unknown(self):
        """Test get_pdu_name for unknown command."""
        with pytest.raises(SMPPPDUException):
            get_pdu_name(0x99999999)


class TestDecodePDU:
    """Test decode_pdu function."""

    def test_decode_enquire_link(self):
        """Test decoding EnquireLink PDU."""
        # Create a basic PDU header for EnquireLink
        import struct

        header = struct.pack('>LLLL', 16, CommandId.ENQUIRE_LINK, 0, 123)

        pdu = decode_pdu(header)
        assert isinstance(pdu, EnquireLink)
        assert pdu.command_id == CommandId.ENQUIRE_LINK
        assert pdu.sequence_number == 123

    def test_decode_invalid_data(self):
        """Test decoding with invalid data."""
        with pytest.raises(SMPPPDUException):
            decode_pdu(b'invalid')


class TestHelperFunctions:
    """Test helper factory functions."""

    def test_create_bind_pdu(self):
        """Test create_bind_pdu helper."""
        pdu = create_bind_pdu('transmitter', system_id='test', password='pass')
        assert isinstance(pdu, BindTransmitter)
        assert pdu.system_id == 'test'
        assert pdu.password == 'pass'

    def test_create_bind_pdu_invalid_type(self):
        """Test create_bind_pdu with invalid type."""
        with pytest.raises(SMPPPDUException, match='Invalid bind type'):
            create_bind_pdu('invalid', 'system', 'pass')

    def test_create_submit_sm_pdu(self):
        """Test create_submit_sm_pdu helper."""
        pdu = create_submit_sm_pdu(
            source_addr='12345', destination_addr='67890', short_message=b'Hello'
        )
        assert isinstance(pdu, SubmitSm)
        assert pdu.source_addr == '12345'
        assert pdu.destination_addr == '67890'
        assert pdu.short_message == b'Hello'

    def test_create_enquire_link_pdu(self):
        """Test create_enquire_link_pdu helper."""
        pdu = create_enquire_link_pdu()
        assert isinstance(pdu, EnquireLink)
        assert pdu.command_id == CommandId.ENQUIRE_LINK

    def test_create_generic_nack_pdu(self):
        """Test create_generic_nack_pdu helper."""
        pdu = create_generic_nack_pdu(42, CommandStatus.ESME_RINVCMDID)
        assert isinstance(pdu, GenericNack)
        assert pdu.sequence_number == 42
        assert pdu.command_status == CommandStatus.ESME_RINVCMDID
