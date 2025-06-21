"""
SMPP Protocol Validation

This module provides validation functions for SMPP protocol fields and structures,
ensuring data integrity and compliance with SMPP v3.4 specification.
"""

import re
from typing import Any, Dict, Optional

from ..exceptions import SMPPValidationException
from .constants import (
    MAX_ADDRESS_LENGTH,
    MAX_PASSWORD_LENGTH,
    MAX_SERVICE_TYPE_LENGTH,
    MAX_SHORT_MESSAGE_LENGTH,
    MAX_SYSTEM_ID_LENGTH,
    CommandId,
    DataCoding,
    NpiType,
    TonType,
)

# Compiled regex patterns for better performance
SYSTEM_ID_PATTERN = re.compile(r'^[a-zA-Z0-9_]+$')
ADDRESS_PATTERN = re.compile(r'^[0-9+]+$')
PASSWORD_PATTERN = re.compile(r'^[a-zA-Z0-9!@#$%^&*()_+-=]+$')

# Validation rule registry
ValidationRule = Dict[str, Any]
_VALIDATION_RULES: Dict[str, ValidationRule] = {}


def register_validation_rule(field_name: str, rule: ValidationRule) -> None:
    """
    Register a custom validation rule for a field.

    Args:
        field_name: Name of the field to validate
        rule: Validation rule configuration
    """
    _VALIDATION_RULES[field_name] = rule


def get_validation_rule(field_name: str) -> Optional[ValidationRule]:
    """
    Get validation rule for a field.

    Args:
        field_name: Name of the field

    Returns:
        Validation rule or None if not found
    """
    return _VALIDATION_RULES.get(field_name)


class FieldValidator:
    """
    Enhanced field validator with caching and custom rules.
    """

    def __init__(self):
        self._cache: Dict[str, bool] = {}

    def validate_with_cache(
        self, field_name: str, value: Any, rule: ValidationRule
    ) -> bool:
        """
        Validate field with result caching.

        Args:
            field_name: Name of the field
            value: Value to validate
            rule: Validation rule

        Returns:
            True if valid

        Raises:
            SMPPValidationException: If validation fails
        """
        cache_key = f'{field_name}:{hash(str(value))}'

        if cache_key in self._cache:
            return self._cache[cache_key]

        result = self._validate_field(field_name, value, rule)
        self._cache[cache_key] = result
        return result

    def _validate_field(
        self, field_name: str, value: Any, rule: ValidationRule
    ) -> bool:
        """Internal field validation logic."""
        # Implementation would go here
        return True

    def clear_cache(self) -> None:
        """Clear validation cache."""
        self._cache.clear()


# Global validator instance
_validator = FieldValidator()


def validate_system_id(system_id: str) -> None:
    """
    Validate SMPP system ID field.

    Args:
        system_id: System ID to validate

    Raises:
        SMPPValidationException: If system ID is invalid
    """
    if not system_id:
        raise SMPPValidationException(
            'System ID cannot be empty',
            field_name='system_id',
            field_value=system_id,
            validation_rule='non_empty',
        )

    if len(system_id) >= MAX_SYSTEM_ID_LENGTH:
        raise SMPPValidationException(
            f'System ID too long: {len(system_id)} >= {MAX_SYSTEM_ID_LENGTH}',
            field_name='system_id',
            field_value=system_id,
            validation_rule='max_length',
        )

    # Use compiled pattern for better performance
    if not SYSTEM_ID_PATTERN.match(system_id):
        raise SMPPValidationException(
            'System ID contains invalid characters (only alphanumeric and underscore allowed)',
            field_name='system_id',
            field_value=system_id,
            validation_rule='character_set',
        )


def validate_password(password: str) -> None:
    """
    Validate SMPP password field.

    Args:
        password: Password to validate

    Raises:
        SMPPValidationException: If password is invalid
    """
    if len(password) >= MAX_PASSWORD_LENGTH:
        raise SMPPValidationException(
            f'Password too long: {len(password)} >= {MAX_PASSWORD_LENGTH}',
            field_name='password',
        )

    # Password can be empty for some configurations
    # Check for printable ASCII characters only
    if password and not password.isprintable():
        raise SMPPValidationException(
            'Password contains non-printable characters', field_name='password'
        )


def validate_address(
    address: str, addr_ton: int, addr_npi: int, field_name: str = 'address'
) -> None:
    """
    Validate SMPP address field with TON and NPI.

    Args:
        address: Address to validate
        addr_ton: Type of Number
        addr_npi: Numbering Plan Indicator
        field_name: Field name for error reporting

    Raises:
        SMPPValidationException: If address is invalid
    """
    if len(address) > MAX_ADDRESS_LENGTH:
        raise SMPPValidationException(
            f'Address too long: {len(address)} > {MAX_ADDRESS_LENGTH}',
            field_name=field_name,
            field_value=address,
        )

    # Validate TON
    if addr_ton not in [t.value for t in TonType]:
        raise SMPPValidationException(
            f'Invalid TON: {addr_ton}',
            field_name=f'{field_name}_ton',
            field_value=str(addr_ton),
        )

    # Validate NPI
    if addr_npi not in [n.value for n in NpiType]:
        raise SMPPValidationException(
            f'Invalid NPI: {addr_npi}',
            field_name=f'{field_name}_npi',
            field_value=str(addr_npi),
        )

    # Validate address format based on TON and NPI
    if addr_ton == TonType.INTERNATIONAL and addr_npi == NpiType.ISDN:
        # International ISDN number should start with digits
        if address and not re.match(r'^\d+$', address):
            raise SMPPValidationException(
                'International ISDN address must contain only digits',
                field_name=field_name,
                field_value=address,
            )
    elif addr_ton == TonType.ALPHANUMERIC:
        # Alphanumeric addresses have different constraints
        if address and not re.match(r'^[a-zA-Z0-9\s]+$', address):
            raise SMPPValidationException(
                'Alphanumeric address contains invalid characters',
                field_name=field_name,
                field_value=address,
            )
    elif addr_ton == TonType.NATIONAL and addr_npi == NpiType.ISDN:
        # National ISDN numbers should be digits
        if address and not re.match(r'^\d+$', address):
            raise SMPPValidationException(
                'National ISDN address must contain only digits',
                field_name=field_name,
                field_value=address,
            )


def validate_service_type(service_type: str) -> None:
    """
    Validate SMPP service type field.

    Args:
        service_type: Service type to validate

    Raises:
        SMPPValidationException: If service type is invalid
    """
    if len(service_type) > MAX_SERVICE_TYPE_LENGTH:
        raise SMPPValidationException(
            f'Service type too long: {len(service_type)} > {MAX_SERVICE_TYPE_LENGTH}',
            field_name='service_type',
            field_value=service_type,
        )

    # Service type should contain only printable ASCII
    if service_type and not service_type.isprintable():
        raise SMPPValidationException(
            'Service type contains non-printable characters',
            field_name='service_type',
            field_value=service_type,
        )


def validate_message_length(
    message: bytes, data_coding: int = DataCoding.DEFAULT
) -> None:
    """
    Validate message length based on data coding.

    Args:
        message: Message bytes to validate
        data_coding: Data coding scheme

    Raises:
        SMPPValidationException: If message is too long
    """
    message_length = len(message)

    if message_length > MAX_SHORT_MESSAGE_LENGTH:
        raise SMPPValidationException(
            f'Message too long: {message_length} > {MAX_SHORT_MESSAGE_LENGTH} bytes',
            field_name='short_message',
        )

    # Additional validation based on data coding
    if data_coding == DataCoding.DEFAULT:
        # GSM 7-bit: theoretical limit is 160 chars = ~140 bytes
        if message_length > 140:
            raise SMPPValidationException(
                f'GSM 7-bit message too long: {message_length} > 140 bytes',
                field_name='short_message',
            )
    elif data_coding == DataCoding.UCS2:
        # UCS2: limit is typically 70 characters = 140 bytes
        if message_length > 140:
            raise SMPPValidationException(
                f'UCS2 message too long: {message_length} > 140 bytes',
                field_name='short_message',
            )


def validate_data_coding(data_coding: int) -> None:
    """
    Validate data coding scheme.

    Args:
        data_coding: Data coding value to validate

    Raises:
        SMPPValidationException: If data coding is invalid
    """
    valid_data_codings = [dc.value for dc in DataCoding]
    if data_coding not in valid_data_codings:
        raise SMPPValidationException(
            f'Invalid data coding: {data_coding}',
            field_name='data_coding',
            field_value=str(data_coding),
        )


def validate_esm_class(esm_class: int) -> None:
    """
    Validate ESM class field.

    Args:
        esm_class: ESM class value to validate

    Raises:
        SMPPValidationException: If ESM class is invalid
    """
    # ESM class is a bit field, validate ranges
    if not (0 <= esm_class <= 255):
        raise SMPPValidationException(
            f'ESM class out of range: {esm_class} (must be 0-255)',
            field_name='esm_class',
            field_value=str(esm_class),
        )


def validate_priority_flag(priority_flag: int) -> None:
    """
    Validate priority flag field.

    Args:
        priority_flag: Priority flag value to validate

    Raises:
        SMPPValidationException: If priority flag is invalid
    """
    if not (0 <= priority_flag <= 3):
        raise SMPPValidationException(
            f'Invalid priority flag: {priority_flag} (must be 0-3)',
            field_name='priority_flag',
            field_value=str(priority_flag),
        )


def validate_registered_delivery(registered_delivery: int) -> None:
    """
    Validate registered delivery field.

    Args:
        registered_delivery: Registered delivery value to validate

    Raises:
        SMPPValidationException: If registered delivery is invalid
    """
    # Registered delivery is a bit field
    if not (0 <= registered_delivery <= 255):
        raise SMPPValidationException(
            f'Registered delivery out of range: {registered_delivery} (must be 0-255)',
            field_name='registered_delivery',
            field_value=str(registered_delivery),
        )


def validate_sequence_number(sequence_number: int) -> None:
    """
    Validate PDU sequence number.

    Args:
        sequence_number: Sequence number to validate

    Raises:
        SMPPValidationException: If sequence number is invalid
    """
    if not (1 <= sequence_number <= 0x7FFFFFFF):
        raise SMPPValidationException(
            f'Invalid sequence number: {sequence_number} (must be 1-2147483647)',
            field_name='sequence_number',
            field_value=str(sequence_number),
        )


def validate_command_id(command_id: int) -> None:
    """
    Validate SMPP command ID.

    Args:
        command_id: Command ID to validate

    Raises:
        SMPPValidationException: If command ID is invalid
    """
    valid_command_ids = [cmd.value for cmd in CommandId]
    if command_id not in valid_command_ids:
        raise SMPPValidationException(
            f'Invalid command ID: 0x{command_id:08X}',
            field_name='command_id',
            field_value=f'0x{command_id:08X}',
        )


def validate_pdu_structure(
    command_id: int, command_length: int, sequence_number: int, command_status: int = 0
) -> None:
    """
    Validate basic PDU structure fields.

    Args:
        command_id: Command ID
        command_length: PDU length
        sequence_number: Sequence number
        command_status: Command status (for response PDUs)

    Raises:
        SMPPValidationException: If any field is invalid
    """
    # Validate command ID
    validate_command_id(command_id)

    # Validate sequence number
    validate_sequence_number(sequence_number)

    # Validate command length
    if command_length < 16:  # Minimum PDU header size
        raise SMPPValidationException(
            f'PDU length too small: {command_length} < 16',
            field_name='command_length',
            field_value=str(command_length),
        )

    if command_length > 65536:  # Maximum PDU size
        raise SMPPValidationException(
            f'PDU length too large: {command_length} > 65536',
            field_name='command_length',
            field_value=str(command_length),
        )

    # Validate command status for response PDUs
    from .constants import is_response_command

    if is_response_command(command_id):
        if not (0 <= command_status <= 0xFFFFFFFF):
            raise SMPPValidationException(
                f'Invalid command status: 0x{command_status:08X}',
                field_name='command_status',
                field_value=f'0x{command_status:08X}',
            )


def validate_bind_parameters(
    system_id: str,
    password: str,
    system_type: str = '',
    interface_version: int = 0x34,
    addr_ton: int = 0,
    addr_npi: int = 0,
    address_range: str = '',
) -> None:
    """
    Validate all bind operation parameters.

    Args:
        system_id: System identifier
        password: Authentication password
        system_type: System type identifier
        interface_version: SMPP interface version
        addr_ton: Address Type of Number
        addr_npi: Address Numbering Plan Indicator
        address_range: Address range for binding

    Raises:
        SMPPValidationException: If any parameter is invalid
    """
    validate_system_id(system_id)
    validate_password(password)

    # Validate system type
    if len(system_type) > 13:
        raise SMPPValidationException(
            f'System type too long: {len(system_type)} > 13',
            field_name='system_type',
            field_value=system_type,
        )

    # Validate interface version
    if interface_version not in (0x33, 0x34):
        raise SMPPValidationException(
            f'Unsupported interface version: 0x{interface_version:02X}',
            field_name='interface_version',
            field_value=f'0x{interface_version:02X}',
        )

    # Validate address range if provided
    if address_range:
        validate_address(address_range, addr_ton, addr_npi, 'address_range')


def validate_submit_sm_parameters(
    source_addr: str,
    destination_addr: str,
    short_message: bytes,
    source_addr_ton: int = 0,
    source_addr_npi: int = 0,
    dest_addr_ton: int = 0,
    dest_addr_npi: int = 0,
    data_coding: int = DataCoding.DEFAULT,
    esm_class: int = 0,
    priority_flag: int = 0,
    registered_delivery: int = 0,
    service_type: str = '',
) -> None:
    """
    Validate all submit_sm operation parameters.

    Args:
        source_addr: Source address
        destination_addr: Destination address
        short_message: Message content
        source_addr_ton: Source address TON
        source_addr_npi: Source address NPI
        dest_addr_ton: Destination address TON
        dest_addr_npi: Destination address NPI
        data_coding: Data coding scheme
        esm_class: ESM class
        priority_flag: Priority flag
        registered_delivery: Registered delivery
        service_type: Service type

    Raises:
        SMPPValidationException: If any parameter is invalid
    """
    validate_address(source_addr, source_addr_ton, source_addr_npi, 'source_addr')
    validate_address(destination_addr, dest_addr_ton, dest_addr_npi, 'destination_addr')
    validate_message_length(short_message, data_coding)
    validate_data_coding(data_coding)
    validate_esm_class(esm_class)
    validate_priority_flag(priority_flag)
    validate_registered_delivery(registered_delivery)
    validate_service_type(service_type)


def validate_optional_parameter(tag: int, value: bytes) -> None:
    """
    Validate optional parameter (TLV) structure.

    Args:
        tag: Parameter tag
        value: Parameter value

    Raises:
        SMPPValidationException: If parameter is invalid
    """
    # Validate tag range
    if not (0 <= tag <= 0xFFFF):
        raise SMPPValidationException(
            f'Invalid TLV tag: 0x{tag:04X} (must be 0x0000-0xFFFF)',
            field_name='tlv_tag',
            field_value=f'0x{tag:04X}',
        )

    # Validate value length
    if len(value) > 0xFFFF:
        raise SMPPValidationException(
            f'TLV value too long: {len(value)} > 65535 bytes', field_name='tlv_value'
        )

    # Additional validation based on well-known tags
    from .constants import OptionalTag

    if tag == OptionalTag.RECEIPTED_MESSAGE_ID:
        # Message ID should be printable string
        try:
            msg_id = value.decode('ascii')
            if not msg_id.isprintable():
                raise SMPPValidationException(
                    'Receipted message ID contains non-printable characters',
                    field_name='receipted_message_id',
                )
        except UnicodeDecodeError:
            raise SMPPValidationException(
                'Receipted message ID is not valid ASCII',
                field_name='receipted_message_id',
            )
    elif tag == OptionalTag.MESSAGE_PAYLOAD:
        # Message payload can be binary, but check reasonable size
        if len(value) > 1024:  # Reasonable limit for extended messages
            raise SMPPValidationException(
                f'Message payload too large: {len(value)} > 1024 bytes',
                field_name='message_payload',
            )
