"""
Unit tests for SMPP Protocol Validation functions.

Tests all validation functions in src/smpp/protocol/validation.py including
field validators, parameter validation, PDU structure validation, and
custom validation rule management.
"""

import pytest
from smpp.protocol import validation
from smpp.protocol.constants import (
    MAX_ADDRESS_LENGTH,
    MAX_PASSWORD_LENGTH,
    MAX_SERVICE_TYPE_LENGTH,
    MAX_SHORT_MESSAGE_LENGTH,
    MAX_SYSTEM_ID_LENGTH,
    CommandId,
    DataCoding,
    NpiType,
    TonType,
    OptionalTag,
)
from smpp.exceptions import SMPPValidationException


class TestValidationRuleRegistry:
    """Tests for validation rule registry functions."""

    def test_register_validation_rule(self):
        """Test registering a custom validation rule."""
        rule = {'min_length': 5, 'max_length': 10}
        validation.register_validation_rule('test_field', rule)

        retrieved_rule = validation.get_validation_rule('test_field')
        assert retrieved_rule == rule

    def test_get_validation_rule_not_found(self):
        """Test getting a non-existent validation rule."""
        result = validation.get_validation_rule('non_existent_field')
        assert result is None

    def test_overwrite_validation_rule(self):
        """Test overwriting an existing validation rule."""
        rule1 = {'type': 'string'}
        rule2 = {'type': 'integer'}

        validation.register_validation_rule('test_field', rule1)
        validation.register_validation_rule('test_field', rule2)

        retrieved_rule = validation.get_validation_rule('test_field')
        assert retrieved_rule == rule2


class TestFieldValidator:
    """Tests for FieldValidator class."""

    def test_field_validator_initialization(self):
        """Test FieldValidator initialization."""
        validator = validation.FieldValidator()
        assert validator._cache == {}

    def test_validate_with_cache(self):
        """Test validation with caching."""
        validator = validation.FieldValidator()
        rule = {'type': 'string'}

        # First call should compute and cache result
        result1 = validator.validate_with_cache('test_field', 'value', rule)
        assert result1 is True

        # Second call should use cached result
        result2 = validator.validate_with_cache('test_field', 'value', rule)
        assert result2 is True

    def test_clear_cache(self):
        """Test clearing validation cache."""
        validator = validation.FieldValidator()
        rule = {'type': 'string'}

        validator.validate_with_cache('test_field', 'value', rule)
        assert len(validator._cache) > 0

        validator.clear_cache()
        assert validator._cache == {}


class TestSystemIdValidation:
    """Tests for validate_system_id function."""

    def test_validate_system_id_valid(self):
        """Test validating a valid system ID."""
        # Should not raise any exception
        validation.validate_system_id('TestSystem123')
        validation.validate_system_id('sys_id_1')
        validation.validate_system_id('A1B2C3')

    def test_validate_system_id_empty(self):
        """Test validating an empty system ID."""
        with pytest.raises(SMPPValidationException, match='System ID cannot be empty'):
            validation.validate_system_id('')

    def test_validate_system_id_too_long(self):
        """Test validating a system ID that's too long."""
        long_id = 'a' * MAX_SYSTEM_ID_LENGTH
        with pytest.raises(SMPPValidationException, match='System ID too long'):
            validation.validate_system_id(long_id)

    def test_validate_system_id_invalid_characters(self):
        """Test validating a system ID with invalid characters."""
        with pytest.raises(SMPPValidationException, match='invalid characters'):
            validation.validate_system_id('system-id')  # Hyphen not allowed

        with pytest.raises(SMPPValidationException, match='invalid characters'):
            validation.validate_system_id('system@id')  # @ not allowed

        with pytest.raises(SMPPValidationException, match='invalid characters'):
            validation.validate_system_id('system id')  # Space not allowed

    def test_validate_system_id_underscore_allowed(self):
        """Test that underscores are allowed in system ID."""
        # Should not raise any exception
        validation.validate_system_id('system_id_123')


class TestPasswordValidation:
    """Tests for validate_password function."""

    def test_validate_password_valid(self):
        """Test validating valid passwords."""
        # Should not raise any exception
        validation.validate_password('password')
        validation.validate_password('Pass123!')
        validation.validate_password('')  # Empty password allowed

    def test_validate_password_too_long(self):
        """Test validating a password that's too long."""
        long_password = 'a' * MAX_PASSWORD_LENGTH
        with pytest.raises(SMPPValidationException, match='Password too long'):
            validation.validate_password(long_password)

    def test_validate_password_non_printable(self):
        """Test validating a password with non-printable characters."""
        with pytest.raises(SMPPValidationException, match='non-printable characters'):
            validation.validate_password('pass\x00')  # Null character (8 chars total)

        with pytest.raises(SMPPValidationException, match='non-printable characters'):
            validation.validate_password('pas\tord')  # Tab character (7 chars total)

    def test_validate_password_special_characters(self):
        """Test that special printable characters are allowed."""
        # Should not raise any exception (using shorter passwords within limit)
        validation.validate_password('P@ssw0rd')  # 8 chars
        validation.validate_password('test#123')  # 7 chars


class TestAddressValidation:
    """Tests for validate_address function."""

    def test_validate_address_valid_international_isdn(self):
        """Test validating a valid international ISDN address."""
        # Should not raise any exception
        validation.validate_address('1234567890', TonType.INTERNATIONAL, NpiType.ISDN)

    def test_validate_address_valid_national_isdn(self):
        """Test validating a valid national ISDN address."""
        # Should not raise any exception
        validation.validate_address('123456', TonType.NATIONAL, NpiType.ISDN)

    def test_validate_address_valid_alphanumeric(self):
        """Test validating a valid alphanumeric address."""
        # Should not raise any exception
        validation.validate_address('TEST123', TonType.ALPHANUMERIC, NpiType.UNKNOWN)
        validation.validate_address(
            'Service Name', TonType.ALPHANUMERIC, NpiType.UNKNOWN
        )

    def test_validate_address_too_long(self):
        """Test validating an address that's too long."""
        long_address = '1' * (MAX_ADDRESS_LENGTH + 1)
        with pytest.raises(SMPPValidationException, match='Address too long'):
            validation.validate_address(
                long_address, TonType.INTERNATIONAL, NpiType.ISDN
            )

    def test_validate_address_invalid_ton(self):
        """Test validating an address with invalid TON."""
        with pytest.raises(SMPPValidationException, match='Invalid TON'):
            validation.validate_address('123456', 99, NpiType.ISDN)

    def test_validate_address_invalid_npi(self):
        """Test validating an address with invalid NPI."""
        with pytest.raises(SMPPValidationException, match='Invalid NPI'):
            validation.validate_address('123456', TonType.INTERNATIONAL, 99)

    def test_validate_address_international_isdn_invalid_format(self):
        """Test validating international ISDN address with invalid format."""
        with pytest.raises(SMPPValidationException, match='must contain only digits'):
            validation.validate_address('123abc', TonType.INTERNATIONAL, NpiType.ISDN)

    def test_validate_address_national_isdn_invalid_format(self):
        """Test validating national ISDN address with invalid format."""
        with pytest.raises(SMPPValidationException, match='must contain only digits'):
            validation.validate_address('123-456', TonType.NATIONAL, NpiType.ISDN)

    def test_validate_address_alphanumeric_invalid_format(self):
        """Test validating alphanumeric address with invalid format."""
        with pytest.raises(SMPPValidationException, match='invalid characters'):
            validation.validate_address(
                'TEST@123', TonType.ALPHANUMERIC, NpiType.UNKNOWN
            )

    def test_validate_address_custom_field_name(self):
        """Test validating address with custom field name in error."""
        with pytest.raises(SMPPValidationException) as exc_info:
            validation.validate_address('', 99, NpiType.ISDN, 'destination_addr')

        assert 'destination_addr_ton' in str(exc_info.value)

    def test_validate_address_empty_valid(self):
        """Test that empty address is valid for some TON/NPI combinations."""
        # Should not raise any exception
        validation.validate_address('', TonType.UNKNOWN, NpiType.UNKNOWN)


class TestServiceTypeValidation:
    """Tests for validate_service_type function."""

    def test_validate_service_type_valid(self):
        """Test validating valid service types."""
        # Should not raise any exception
        validation.validate_service_type('')  # Empty allowed
        validation.validate_service_type('SMS')
        validation.validate_service_type('WAP')

    def test_validate_service_type_too_long(self):
        """Test validating a service type that's too long."""
        long_service_type = 'a' * (MAX_SERVICE_TYPE_LENGTH + 1)
        with pytest.raises(SMPPValidationException, match='Service type too long'):
            validation.validate_service_type(long_service_type)

    def test_validate_service_type_non_printable(self):
        """Test validating a service type with non-printable characters."""
        with pytest.raises(SMPPValidationException, match='non-printable characters'):
            validation.validate_service_type('SMS\x00')


class TestMessageLengthValidation:
    """Tests for validate_message_length function."""

    def test_validate_message_length_valid_default(self):
        """Test validating valid message length with default data coding."""
        message = b'Hello World'
        # Should not raise any exception
        validation.validate_message_length(message, DataCoding.DEFAULT)

    def test_validate_message_length_valid_ucs2(self):
        """Test validating valid message length with UCS2 data coding."""
        message = b'Hello World'
        # Should not raise any exception
        validation.validate_message_length(message, DataCoding.UCS2)

    def test_validate_message_length_too_long_general(self):
        """Test validating a message that exceeds the general maximum."""
        long_message = b'a' * (MAX_SHORT_MESSAGE_LENGTH + 1)
        with pytest.raises(SMPPValidationException, match='Message too long'):
            validation.validate_message_length(long_message)

    def test_validate_message_length_too_long_gsm_7bit(self):
        """Test validating a message that exceeds GSM 7-bit limit."""
        long_message = b'a' * 141  # > 140 bytes
        with pytest.raises(SMPPValidationException, match='GSM 7-bit message too long'):
            validation.validate_message_length(long_message, DataCoding.DEFAULT)

    def test_validate_message_length_too_long_ucs2(self):
        """Test validating a message that exceeds UCS2 limit."""
        long_message = b'a' * 141  # > 140 bytes
        with pytest.raises(SMPPValidationException, match='UCS2 message too long'):
            validation.validate_message_length(long_message, DataCoding.UCS2)

    def test_validate_message_length_boundary_gsm_7bit(self):
        """Test validating a message at the GSM 7-bit boundary."""
        message = b'a' * 140  # Exactly 140 bytes
        # Should not raise any exception
        validation.validate_message_length(message, DataCoding.DEFAULT)

    def test_validate_message_length_boundary_ucs2(self):
        """Test validating a message at the UCS2 boundary."""
        message = b'a' * 140  # Exactly 140 bytes
        # Should not raise any exception
        validation.validate_message_length(message, DataCoding.UCS2)


class TestDataCodingValidation:
    """Tests for validate_data_coding function."""

    def test_validate_data_coding_valid(self):
        """Test validating valid data coding schemes."""
        # Should not raise any exception
        validation.validate_data_coding(DataCoding.DEFAULT)
        validation.validate_data_coding(DataCoding.IA5_ASCII)
        validation.validate_data_coding(DataCoding.LATIN_1)
        validation.validate_data_coding(DataCoding.UCS2)

    def test_validate_data_coding_invalid(self):
        """Test validating invalid data coding schemes."""
        with pytest.raises(SMPPValidationException, match='Invalid data coding'):
            validation.validate_data_coding(99)

        with pytest.raises(SMPPValidationException, match='Invalid data coding'):
            validation.validate_data_coding(-1)


class TestEsmClassValidation:
    """Tests for validate_esm_class function."""

    def test_validate_esm_class_valid(self):
        """Test validating valid ESM class values."""
        # Should not raise any exception
        validation.validate_esm_class(0)
        validation.validate_esm_class(1)
        validation.validate_esm_class(128)
        validation.validate_esm_class(255)

    def test_validate_esm_class_out_of_range_low(self):
        """Test validating ESM class value below valid range."""
        with pytest.raises(SMPPValidationException, match='ESM class out of range'):
            validation.validate_esm_class(-1)

    def test_validate_esm_class_out_of_range_high(self):
        """Test validating ESM class value above valid range."""
        with pytest.raises(SMPPValidationException, match='ESM class out of range'):
            validation.validate_esm_class(256)


class TestPriorityFlagValidation:
    """Tests for validate_priority_flag function."""

    def test_validate_priority_flag_valid(self):
        """Test validating valid priority flag values."""
        # Should not raise any exception
        validation.validate_priority_flag(0)
        validation.validate_priority_flag(1)
        validation.validate_priority_flag(2)
        validation.validate_priority_flag(3)

    def test_validate_priority_flag_invalid_low(self):
        """Test validating priority flag value below valid range."""
        with pytest.raises(SMPPValidationException, match='Invalid priority flag'):
            validation.validate_priority_flag(-1)

    def test_validate_priority_flag_invalid_high(self):
        """Test validating priority flag value above valid range."""
        with pytest.raises(SMPPValidationException, match='Invalid priority flag'):
            validation.validate_priority_flag(4)


class TestRegisteredDeliveryValidation:
    """Tests for validate_registered_delivery function."""

    def test_validate_registered_delivery_valid(self):
        """Test validating valid registered delivery values."""
        # Should not raise any exception
        validation.validate_registered_delivery(0)
        validation.validate_registered_delivery(1)
        validation.validate_registered_delivery(128)
        validation.validate_registered_delivery(255)

    def test_validate_registered_delivery_out_of_range_low(self):
        """Test validating registered delivery value below valid range."""
        with pytest.raises(
            SMPPValidationException, match='Registered delivery out of range'
        ):
            validation.validate_registered_delivery(-1)

    def test_validate_registered_delivery_out_of_range_high(self):
        """Test validating registered delivery value above valid range."""
        with pytest.raises(
            SMPPValidationException, match='Registered delivery out of range'
        ):
            validation.validate_registered_delivery(256)


class TestSequenceNumberValidation:
    """Tests for validate_sequence_number function."""

    def test_validate_sequence_number_valid(self):
        """Test validating valid sequence numbers."""
        # Should not raise any exception
        validation.validate_sequence_number(1)
        validation.validate_sequence_number(12345)
        validation.validate_sequence_number(0x7FFFFFFF)  # Maximum value

    def test_validate_sequence_number_zero(self):
        """Test validating sequence number zero."""
        with pytest.raises(SMPPValidationException, match='Invalid sequence number'):
            validation.validate_sequence_number(0)

    def test_validate_sequence_number_negative(self):
        """Test validating negative sequence number."""
        with pytest.raises(SMPPValidationException, match='Invalid sequence number'):
            validation.validate_sequence_number(-1)

    def test_validate_sequence_number_too_large(self):
        """Test validating sequence number that's too large."""
        with pytest.raises(SMPPValidationException, match='Invalid sequence number'):
            validation.validate_sequence_number(0x80000000)  # Too large


class TestCommandIdValidation:
    """Tests for validate_command_id function."""

    def test_validate_command_id_valid(self):
        """Test validating valid command IDs."""
        # Should not raise any exception
        validation.validate_command_id(CommandId.BIND_TRANSMITTER)
        validation.validate_command_id(CommandId.SUBMIT_SM)
        validation.validate_command_id(CommandId.ENQUIRE_LINK)

    def test_validate_command_id_invalid(self):
        """Test validating invalid command IDs."""
        with pytest.raises(SMPPValidationException, match='Invalid command ID'):
            validation.validate_command_id(0x99999999)

        with pytest.raises(SMPPValidationException, match='Invalid command ID'):
            validation.validate_command_id(0)


class TestPDUStructureValidation:
    """Tests for validate_pdu_structure function."""

    def test_validate_pdu_structure_valid_request(self):
        """Test validating valid PDU structure for request."""
        # Should not raise any exception
        validation.validate_pdu_structure(
            CommandId.BIND_TRANSMITTER,
            32,  # command_length
            12345,  # sequence_number
            0,  # command_status
        )

    def test_validate_pdu_structure_valid_response(self):
        """Test validating valid PDU structure for response."""
        # Should not raise any exception
        validation.validate_pdu_structure(
            CommandId.BIND_TRANSMITTER_RESP,
            32,  # command_length
            12345,  # sequence_number
            0,  # command_status
        )

    def test_validate_pdu_structure_invalid_command_id(self):
        """Test validating PDU structure with invalid command ID."""
        with pytest.raises(SMPPValidationException, match='Invalid command ID'):
            validation.validate_pdu_structure(0x99999999, 32, 12345, 0)

    def test_validate_pdu_structure_invalid_sequence_number(self):
        """Test validating PDU structure with invalid sequence number."""
        with pytest.raises(SMPPValidationException, match='Invalid sequence number'):
            validation.validate_pdu_structure(CommandId.BIND_TRANSMITTER, 32, 0, 0)

    def test_validate_pdu_structure_command_length_too_small(self):
        """Test validating PDU structure with command length too small."""
        with pytest.raises(SMPPValidationException, match='PDU length too small'):
            validation.validate_pdu_structure(CommandId.BIND_TRANSMITTER, 15, 12345, 0)

    def test_validate_pdu_structure_command_length_too_large(self):
        """Test validating PDU structure with command length too large."""
        with pytest.raises(SMPPValidationException, match='PDU length too large'):
            validation.validate_pdu_structure(
                CommandId.BIND_TRANSMITTER, 65537, 12345, 0
            )

    def test_validate_pdu_structure_invalid_command_status_response(self):
        """Test validating PDU structure with invalid command status for response."""
        with pytest.raises(SMPPValidationException, match='Invalid command status'):
            validation.validate_pdu_structure(
                CommandId.BIND_TRANSMITTER_RESP, 32, 12345, -1
            )


class TestBindParametersValidation:
    """Tests for validate_bind_parameters function."""

    def test_validate_bind_parameters_valid(self):
        """Test validating valid bind parameters."""
        # Should not raise any exception
        validation.validate_bind_parameters(
            system_id='TestSystem',
            password='password',
            system_type='SMS',
            interface_version=0x34,
            addr_ton=TonType.UNKNOWN,
            addr_npi=NpiType.UNKNOWN,
            address_range='',
        )

    def test_validate_bind_parameters_system_type_too_long(self):
        """Test validating bind parameters with system type too long."""
        with pytest.raises(SMPPValidationException, match='System type too long'):
            validation.validate_bind_parameters(
                system_id='TestSystem',
                password='password',
                system_type='a' * 14,  # > 13 characters
            )

    def test_validate_bind_parameters_invalid_interface_version(self):
        """Test validating bind parameters with invalid interface version."""
        with pytest.raises(
            SMPPValidationException, match='Unsupported interface version'
        ):
            validation.validate_bind_parameters(
                system_id='TestSystem',
                password='password',
                interface_version=0x32,  # Unsupported version
            )

    def test_validate_bind_parameters_valid_interface_versions(self):
        """Test validating bind parameters with valid interface versions."""
        # Should not raise any exception
        validation.validate_bind_parameters(
            system_id='TestSystem', password='password', interface_version=0x33
        )

        validation.validate_bind_parameters(
            system_id='TestSystem', password='password', interface_version=0x34
        )

    def test_validate_bind_parameters_invalid_address_range(self):
        """Test validating bind parameters with invalid address range."""
        with pytest.raises(SMPPValidationException):
            validation.validate_bind_parameters(
                system_id='TestSystem',
                password='password',
                addr_ton=TonType.INTERNATIONAL,
                addr_npi=NpiType.ISDN,
                address_range='abc123',  # Invalid for international ISDN
            )


class TestSubmitSmParametersValidation:
    """Tests for validate_submit_sm_parameters function."""

    def test_validate_submit_sm_parameters_valid(self):
        """Test validating valid submit_sm parameters."""
        # Should not raise any exception
        validation.validate_submit_sm_parameters(
            source_addr='1234567890',
            destination_addr='0987654321',
            short_message=b'Hello World',
            source_addr_ton=TonType.INTERNATIONAL,
            source_addr_npi=NpiType.ISDN,
            dest_addr_ton=TonType.INTERNATIONAL,
            dest_addr_npi=NpiType.ISDN,
            data_coding=DataCoding.DEFAULT,
            esm_class=0,
            priority_flag=0,
            registered_delivery=0,
            service_type='SMS',
        )

    def test_validate_submit_sm_parameters_invalid_source_address(self):
        """Test validating submit_sm parameters with invalid source address."""
        with pytest.raises(SMPPValidationException):
            validation.validate_submit_sm_parameters(
                source_addr='abc123',  # Invalid for international ISDN
                destination_addr='0987654321',
                short_message=b'Hello World',
                source_addr_ton=TonType.INTERNATIONAL,
                source_addr_npi=NpiType.ISDN,
            )

    def test_validate_submit_sm_parameters_invalid_destination_address(self):
        """Test validating submit_sm parameters with invalid destination address."""
        with pytest.raises(SMPPValidationException):
            validation.validate_submit_sm_parameters(
                source_addr='1234567890',
                destination_addr='abc123',  # Invalid for international ISDN
                short_message=b'Hello World',
                dest_addr_ton=TonType.INTERNATIONAL,
                dest_addr_npi=NpiType.ISDN,
            )

    def test_validate_submit_sm_parameters_message_too_long(self):
        """Test validating submit_sm parameters with message too long."""
        long_message = b'a' * (MAX_SHORT_MESSAGE_LENGTH + 1)
        with pytest.raises(SMPPValidationException, match='Message too long'):
            validation.validate_submit_sm_parameters(
                source_addr='1234567890',
                destination_addr='0987654321',
                short_message=long_message,
            )

    def test_validate_submit_sm_parameters_invalid_data_coding(self):
        """Test validating submit_sm parameters with invalid data coding."""
        with pytest.raises(SMPPValidationException, match='Invalid data coding'):
            validation.validate_submit_sm_parameters(
                source_addr='1234567890',
                destination_addr='0987654321',
                short_message=b'Hello World',
                data_coding=99,
            )

    def test_validate_submit_sm_parameters_invalid_priority_flag(self):
        """Test validating submit_sm parameters with invalid priority flag."""
        with pytest.raises(SMPPValidationException, match='Invalid priority flag'):
            validation.validate_submit_sm_parameters(
                source_addr='1234567890',
                destination_addr='0987654321',
                short_message=b'Hello World',
                priority_flag=4,
            )


class TestOptionalParameterValidation:
    """Tests for validate_optional_parameter function."""

    def test_validate_optional_parameter_valid(self):
        """Test validating valid optional parameters."""
        # Should not raise any exception
        validation.validate_optional_parameter(0x001E, b'message123')
        validation.validate_optional_parameter(0x0001, b'test')

    def test_validate_optional_parameter_invalid_tag_negative(self):
        """Test validating optional parameter with negative tag."""
        with pytest.raises(SMPPValidationException, match='Invalid TLV tag'):
            validation.validate_optional_parameter(-1, b'value')

    def test_validate_optional_parameter_invalid_tag_too_large(self):
        """Test validating optional parameter with tag too large."""
        with pytest.raises(SMPPValidationException, match='Invalid TLV tag'):
            validation.validate_optional_parameter(0x10000, b'value')

    def test_validate_optional_parameter_value_too_long(self):
        """Test validating optional parameter with value too long."""
        long_value = b'a' * 0x10000  # 65536 bytes
        with pytest.raises(SMPPValidationException, match='TLV value too long'):
            validation.validate_optional_parameter(0x001E, long_value)

    def test_validate_optional_parameter_receipted_message_id_valid(self):
        """Test validating valid receipted message ID."""
        # Should not raise any exception
        validation.validate_optional_parameter(
            OptionalTag.RECEIPTED_MESSAGE_ID, b'MSG123456789'
        )

    def test_validate_optional_parameter_receipted_message_id_non_printable(self):
        """Test validating receipted message ID with non-printable characters."""
        with pytest.raises(SMPPValidationException, match='non-printable characters'):
            validation.validate_optional_parameter(
                OptionalTag.RECEIPTED_MESSAGE_ID, b'MSG\x00123'
            )

    def test_validate_optional_parameter_receipted_message_id_invalid_ascii(self):
        """Test validating receipted message ID with invalid ASCII."""
        with pytest.raises(SMPPValidationException, match='not valid ASCII'):
            validation.validate_optional_parameter(
                OptionalTag.RECEIPTED_MESSAGE_ID, b'\xff\xfe'
            )

    def test_validate_optional_parameter_message_payload_valid(self):
        """Test validating valid message payload."""
        # Should not raise any exception
        validation.validate_optional_parameter(
            OptionalTag.MESSAGE_PAYLOAD, b'Extended message content'
        )

    def test_validate_optional_parameter_message_payload_too_large(self):
        """Test validating message payload that's too large."""
        large_payload = b'a' * 1025  # > 1024 bytes
        with pytest.raises(SMPPValidationException, match='Message payload too large'):
            validation.validate_optional_parameter(
                OptionalTag.MESSAGE_PAYLOAD, large_payload
            )

    def test_validate_optional_parameter_boundary_values(self):
        """Test validating optional parameters with boundary values."""
        # Should not raise any exception
        validation.validate_optional_parameter(0x0000, b'')  # Minimum tag, empty value
        validation.validate_optional_parameter(0xFFFF, b'')  # Maximum tag, empty value
        validation.validate_optional_parameter(
            0x001E, b'a' * 0xFFFF
        )  # Maximum value length


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_system_id_boundary_length(self):
        """Test system ID at exact boundary length."""
        # Should not raise any exception
        boundary_id = 'a' * (MAX_SYSTEM_ID_LENGTH - 1)
        validation.validate_system_id(boundary_id)

    def test_password_boundary_length(self):
        """Test password at exact boundary length."""
        # Should not raise any exception (8 chars, just under limit of 9)
        boundary_password = 'a' * (MAX_PASSWORD_LENGTH - 1)
        validation.validate_password(boundary_password)

    def test_address_boundary_length(self):
        """Test address at exact boundary length."""
        # Should not raise any exception
        boundary_address = '1' * MAX_ADDRESS_LENGTH
        validation.validate_address(
            boundary_address, TonType.INTERNATIONAL, NpiType.ISDN
        )

    def test_service_type_boundary_length(self):
        """Test service type at exact boundary length."""
        # Should not raise any exception
        boundary_service_type = 'a' * MAX_SERVICE_TYPE_LENGTH
        validation.validate_service_type(boundary_service_type)

    def test_message_boundary_length(self):
        """Test message at exact boundary length for GSM 7-bit."""
        # Should not raise any exception (use 140 bytes for GSM 7-bit)
        boundary_message = b'a' * 140  # GSM 7-bit limit
        validation.validate_message_length(boundary_message, DataCoding.DEFAULT)

    def test_message_general_boundary_length(self):
        """Test message at exact general boundary length."""
        # Should not raise any exception (use general MAX_SHORT_MESSAGE_LENGTH for other coding)
        boundary_message = b'a' * MAX_SHORT_MESSAGE_LENGTH
        validation.validate_message_length(
            boundary_message, DataCoding.LATIN_1
        )  # Non-GSM coding

    def test_sequence_number_boundary_values(self):
        """Test sequence number at boundary values."""
        # Should not raise any exception
        validation.validate_sequence_number(1)  # Minimum valid
        validation.validate_sequence_number(0x7FFFFFFF)  # Maximum valid

    def test_multiple_validation_errors(self):
        """Test that validation stops at first error."""
        # Should raise exception for first error encountered
        with pytest.raises(SMPPValidationException):
            validation.validate_bind_parameters(
                system_id='',  # This will cause the first error
                password='a' * MAX_PASSWORD_LENGTH,  # This would also be an error
                interface_version=0x32,  # This would also be an error
            )


class TestRealWorldScenarios:
    """Tests for real-world usage scenarios."""

    def test_complete_bind_flow(self):
        """Test complete bind parameter validation flow."""
        # Should not raise any exception (using shorter password)
        validation.validate_bind_parameters(
            system_id='Client1',
            password='Secret',  # 6 chars, within limit
            system_type='SMS_GW',  # 6 chars, within limit
            interface_version=0x34,
            addr_ton=TonType.INTERNATIONAL,
            addr_npi=NpiType.ISDN,
            address_range='1234567890',
        )

    def test_complete_submit_sm_flow(self):
        """Test complete submit_sm parameter validation flow."""
        # Should not raise any exception
        validation.validate_submit_sm_parameters(
            source_addr='12345',
            destination_addr='67890',
            short_message=b'Test message content',
            source_addr_ton=TonType.NATIONAL,
            source_addr_npi=NpiType.ISDN,
            dest_addr_ton=TonType.INTERNATIONAL,
            dest_addr_npi=NpiType.ISDN,
            data_coding=DataCoding.DEFAULT,
            esm_class=0,
            priority_flag=1,
            registered_delivery=1,
            service_type='SMS',
        )

    def test_alphanumeric_addressing(self):
        """Test alphanumeric addressing validation."""
        # Should not raise any exception
        validation.validate_address('SERVICE', TonType.ALPHANUMERIC, NpiType.UNKNOWN)
        validation.validate_address('TEST 123', TonType.ALPHANUMERIC, NpiType.UNKNOWN)

    def test_unicode_message_validation(self):
        """Test Unicode message validation."""
        unicode_message = 'Hello 🌍'.encode('utf-16-be')
        # Should not raise any exception
        validation.validate_message_length(unicode_message, DataCoding.UCS2)

    def test_empty_fields_allowed(self):
        """Test that empty fields are allowed where appropriate."""
        # Should not raise any exception
        validation.validate_password('')  # Empty password allowed
        validation.validate_service_type('')  # Empty service type allowed
        validation.validate_address(
            '', TonType.UNKNOWN, NpiType.UNKNOWN
        )  # Empty address allowed
