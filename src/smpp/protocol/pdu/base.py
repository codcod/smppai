"""
SMPP PDU Base Classes and Utilities

This module contains the base PDU class and common utilities for encoding/decoding
SMPP protocol data units according to the SMPP v3.4 specification.

The module provides:
- PDU: Abstract base class for all SMPP PDUs
- TLVParameter: Type-Length-Value parameter implementation
- Specialized base classes for different PDU types
- Validation and encoding/decoding utilities
"""

import struct
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, List, Optional, Tuple

from ...exceptions import SMPPPDUException
from ..constants import MAX_PDU_SIZE, PDU_HEADER_SIZE, CommandStatus
from ..validation import validate_optional_parameter


class TLVParameter:
    """
    Tag-Length-Value parameter for optional parameters.

    TLV parameters are used in SMPP to encode optional fields in PDUs.
    Each parameter consists of a 16-bit tag, 16-bit length, and variable-length value.

    Attributes:
        tag: The parameter tag identifier (0-65535)
        length: The length of the value in bytes
        value: The parameter value as bytes
    """

    def __init__(self, tag: int, value: bytes) -> None:
        """
        Initialize TLV parameter.

        Args:
            tag: Parameter tag identifier
            value: Parameter value as bytes

        Raises:
            SMPPPDUException: If tag is invalid or value is too long
        """
        if not (0 <= tag <= 0xFFFF):
            raise SMPPPDUException(f'Invalid TLV tag: {tag}')
        if len(value) > 0xFFFF:
            raise SMPPPDUException(f'TLV value too long: {len(value)} bytes')

        # Validate TLV parameter for protocol compliance
        validate_optional_parameter(tag, value)

        self.tag = tag
        self.length = len(value)
        self.value = value

    def encode(self) -> bytes:
        """
        Encode TLV parameter to bytes.

        Returns:
            The encoded TLV parameter as bytes
        """
        # Use bytearray for better performance when building larger data structures
        result = bytearray(4 + len(self.value))
        struct.pack_into('>HH', result, 0, self.tag, self.length)
        result[4:] = self.value
        return bytes(result)

    @classmethod
    def decode(cls, data: bytes, offset: int = 0) -> Tuple['TLVParameter', int]:
        """
        Decode TLV parameter from bytes.

        Args:
            data: The byte data to decode from
            offset: Starting offset in the data

        Returns:
            Tuple of (TLVParameter instance, new offset)

        Raises:
            SMPPPDUException: If data is insufficient or invalid
        """
        if len(data) - offset < 4:
            raise SMPPPDUException('Insufficient data for TLV header')

        tag, length = struct.unpack('>HH', data[offset : offset + 4])
        if len(data) - offset < 4 + length:
            raise SMPPPDUException('Insufficient data for TLV value')

        value = data[offset + 4 : offset + 4 + length]
        return cls(tag, value), offset + 4 + length

    def __repr__(self) -> str:
        return f'TLVParameter(tag=0x{self.tag:04X}, length={self.length}, value={self.value!r})'

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TLVParameter):
            return False
        return self.tag == other.tag and self.value == other.value

    def __hash__(self) -> int:
        return hash((self.tag, self.value))


@dataclass
class PDU(ABC):
    """
    Abstract base class for all SMPP PDUs.

    This class provides the common functionality for all SMPP Protocol Data Units,
    including header encoding/decoding, optional parameter handling, and validation.

    Attributes:
        command_id: The SMPP command identifier
        command_status: Status code (0 for requests, error code for responses)
        sequence_number: Unique sequence number for request/response matching
        optional_parameters: List of TLV optional parameters
    """

    command_id: int = 0
    command_status: int = CommandStatus.ESME_ROK
    sequence_number: int = 0
    optional_parameters: List[TLVParameter] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Initialize PDU after creation."""
        if self.sequence_number == 0:
            # Generate a unique sequence number if not provided
            self.sequence_number = self._generate_sequence_number()

    @staticmethod
    def _generate_sequence_number() -> int:
        """
        Generate a unique sequence number.

        Returns:
            A unique sequence number between 1 and 0x7FFFFFFF
        """
        return int(time.time() * 1000) % 0x7FFFFFFF

    @abstractmethod
    def encode_body(self) -> bytes:
        """
        Encode PDU body to bytes.

        Must be implemented by subclasses to encode the PDU-specific body data.

        Returns:
            The encoded PDU body as bytes
        """
        pass

    @abstractmethod
    def decode_body(self, data: bytes, offset: int = 0) -> int:
        """
        Decode PDU body from bytes.

        Must be implemented by subclasses to decode the PDU-specific body data.

        Args:
            data: The byte data to decode from
            offset: Starting offset in the data

        Returns:
            The new offset after decoding the body
        """
        pass

    def encode(self) -> bytes:
        """
        Encode complete PDU to bytes.

        Returns:
            The complete encoded PDU including header, body, and optional parameters

        Raises:
            SMPPPDUException: If PDU is invalid or too large
        """
        try:
            body = self.encode_body()
        except Exception as e:
            raise SMPPPDUException(f'Failed to encode PDU body: {e}') from e

        # Encode optional parameters
        optional_data = b''
        for param in self.optional_parameters:
            try:
                optional_data += param.encode()
            except Exception as e:
                raise SMPPPDUException(
                    f'Failed to encode optional parameter 0x{param.tag:04X}: {e}'
                ) from e

        total_length = PDU_HEADER_SIZE + len(body) + len(optional_data)

        # Check maximum PDU size
        if total_length > MAX_PDU_SIZE:
            raise SMPPPDUException(
                f'PDU too large: {total_length} bytes exceeds maximum {MAX_PDU_SIZE}'
            )

        # Encode header
        header = struct.pack(
            '>LLLL',
            total_length,
            self.command_id,
            self.command_status,
            self.sequence_number,
        )

        return header + body + optional_data

    @classmethod
    def decode(cls, data: bytes) -> 'PDU':
        """
        Decode PDU from bytes.

        Args:
            data: The byte data to decode

        Returns:
            The decoded PDU instance

        Raises:
            SMPPPDUException: If data is insufficient or invalid
        """
        if len(data) < PDU_HEADER_SIZE:
            raise SMPPPDUException(
                f'Insufficient data for PDU header: {len(data)} < {PDU_HEADER_SIZE}'
            )

        # Decode header
        try:
            length, command_id, command_status, sequence_number = struct.unpack(
                '>LLLL', data[:PDU_HEADER_SIZE]
            )
        except struct.error as e:
            raise SMPPPDUException(f'Failed to decode PDU header: {e}') from e

        # Validate PDU length
        if len(data) < length:
            raise SMPPPDUException(
                f'PDU length mismatch: expected {length}, got {len(data)}'
            )

        if length > MAX_PDU_SIZE:
            raise SMPPPDUException(
                f'PDU length exceeds maximum: {length} > {MAX_PDU_SIZE}'
            )

        if length < PDU_HEADER_SIZE:
            raise SMPPPDUException(f'Invalid PDU length: {length} < {PDU_HEADER_SIZE}')

        # Get the appropriate PDU class
        from .factory import get_pdu_class

        try:
            pdu_class = get_pdu_class(command_id)
        except Exception as e:
            raise SMPPPDUException(f'Unknown command ID: 0x{command_id:08X}') from e

        # Create PDU instance
        try:
            pdu = pdu_class(
                command_id=command_id,
                command_status=command_status,
                sequence_number=sequence_number,
            )
        except Exception as e:
            raise SMPPPDUException(f'Failed to create PDU instance: {e}') from e

        # Decode body
        try:
            offset = pdu.decode_body(data, PDU_HEADER_SIZE)
        except Exception as e:
            raise SMPPPDUException(f'Failed to decode PDU body: {e}') from e

        # Decode optional parameters
        while offset < length:
            try:
                param, offset = TLVParameter.decode(data, offset)
                pdu.optional_parameters.append(param)
            except Exception as e:
                raise SMPPPDUException(
                    f'Failed to decode optional parameter at offset {offset}: {e}'
                ) from e

        return pdu

    def get_optional_parameter(self, tag: int) -> Optional[TLVParameter]:
        """
        Get optional parameter by tag.

        Args:
            tag: The parameter tag to search for

        Returns:
            The TLV parameter if found, None otherwise
        """
        for param in self.optional_parameters:
            if param.tag == tag:
                return param
        return None

    def add_optional_parameter(self, tag: int, value: bytes) -> None:
        """
        Add optional parameter.

        If a parameter with the same tag already exists, it will be replaced.

        Args:
            tag: The parameter tag
            value: The parameter value as bytes

        Raises:
            SMPPPDUException: If tag or value is invalid
        """
        # Remove existing parameter with same tag
        self.remove_optional_parameter(tag)
        try:
            param = TLVParameter(tag, value)
            self.optional_parameters.append(param)
        except Exception as e:
            raise SMPPPDUException(
                f'Failed to add optional parameter 0x{tag:04X}: {e}'
            ) from e

    def remove_optional_parameter(self, tag: int) -> bool:
        """
        Remove optional parameter by tag.

        Args:
            tag: The parameter tag to remove

        Returns:
            True if parameter was found and removed, False otherwise
        """
        for i, param in enumerate(self.optional_parameters):
            if param.tag == tag:
                del self.optional_parameters[i]
                return True
        return False

    def get_optional_parameter_value(self, tag: int) -> Optional[bytes]:
        """
        Get optional parameter value by tag.

        Args:
            tag: The parameter tag to search for

        Returns:
            The parameter value if found, None otherwise
        """
        param = self.get_optional_parameter(tag)
        return param.value if param else None

    def has_optional_parameter(self, tag: int) -> bool:
        """
        Check if optional parameter exists.

        Args:
            tag: The parameter tag to check for

        Returns:
            True if parameter exists, False otherwise
        """
        return self.get_optional_parameter(tag) is not None

    def clear_optional_parameters(self) -> None:
        """Remove all optional parameters."""
        self.optional_parameters.clear()

    def get_total_length(self) -> int:
        """
        Calculate total PDU length.

        Returns:
            The total length including header, body, and optional parameters
        """
        body_length = len(self.encode_body())
        optional_length = sum(
            4 + len(param.value) for param in self.optional_parameters
        )
        return PDU_HEADER_SIZE + body_length + optional_length

    def is_response(self) -> bool:
        """
        Check if this is a response PDU.

        Returns:
            True if this is a response PDU (command_id has high bit set)
        """
        return bool(self.command_id & 0x80000000)

    def is_request(self) -> bool:
        """
        Check if this is a request PDU.

        Returns:
            True if this is a request PDU (command_id has high bit clear)
        """
        return not self.is_response()

    def get_corresponding_response_command_id(self) -> int:
        """
        Get the command ID for the corresponding response PDU.

        Returns:
            The response command ID

        Raises:
            SMPPPDUException: If this is already a response PDU
        """
        if self.is_response():
            raise SMPPPDUException('PDU is already a response')
        return self.command_id | 0x80000000

    def get_corresponding_request_command_id(self) -> int:
        """
        Get the command ID for the corresponding request PDU.

        Returns:
            The request command ID

        Raises:
            SMPPPDUException: If this is already a request PDU
        """
        if self.is_request():
            raise SMPPPDUException('PDU is already a request')
        return self.command_id & 0x7FFFFFFF

    def validate(self) -> None:
        """
        Validate PDU structure and fields.

        Raises:
            SMPPPDUException: If validation fails
        """
        # Validate sequence number
        if not (1 <= self.sequence_number <= 0x7FFFFFFF):
            raise SMPPPDUException(f'Invalid sequence number: {self.sequence_number}')

        # Validate command status for response PDUs
        if self.is_response() and self.command_status < 0:
            raise SMPPPDUException(f'Invalid command status: {self.command_status}')

        # Validate total length
        try:
            total_length = self.get_total_length()
            if total_length > MAX_PDU_SIZE:
                raise SMPPPDUException(
                    f'PDU too large: {total_length} > {MAX_PDU_SIZE}'
                )
        except Exception as e:
            raise SMPPPDUException(f'Failed to calculate PDU length: {e}') from e

        # Validate optional parameters
        for param in self.optional_parameters:
            if not (0 <= param.tag <= 0xFFFF):
                raise SMPPPDUException(f'Invalid TLV tag: 0x{param.tag:04X}')
            if len(param.value) > 0xFFFF:
                raise SMPPPDUException(f'TLV value too long: {len(param.value)}')

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}('
            f'command_id=0x{self.command_id:08X}, '
            f'command_status=0x{self.command_status:08X}, '
            f'sequence_number={self.sequence_number}, '
            f'optional_parameters={len(self.optional_parameters)})'
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PDU):
            return False
        return (
            self.command_id == other.command_id
            and self.command_status == other.command_status
            and self.sequence_number == other.sequence_number
            and self.optional_parameters == other.optional_parameters
        )

    def __hash__(self) -> int:
        return hash(
            (
                self.command_id,
                self.command_status,
                self.sequence_number,
                tuple(self.optional_parameters),
            )
        )


class RequestPDU(PDU):
    """
    Base class for request PDUs.

    Request PDUs are sent by SMPP clients to servers and always have
    command_status set to 0.
    """

    def __post_init__(self) -> None:
        super().__post_init__()
        # Ensure command_status is 0 for requests
        self.command_status = CommandStatus.ESME_ROK


class ResponsePDU(PDU):
    """
    Base class for response PDUs.

    Response PDUs are sent by SMPP servers to clients in response to requests.
    They contain a command_status field indicating success or error.
    """

    def __init__(
        self, command_status: int = CommandStatus.ESME_ROK, **kwargs: Any
    ) -> None:
        super().__init__(command_status=command_status, **kwargs)

    def create_error_response(
        self, request_pdu: PDU, error_status: int, error_message: Optional[str] = None
    ) -> 'ResponsePDU':
        """
        Create an error response for a request PDU.

        Args:
            request_pdu: The original request PDU
            error_status: The error status code
            error_message: Optional error message

        Returns:
            This response PDU configured as an error response
        """
        self.sequence_number = request_pdu.sequence_number
        self.command_status = error_status

        if error_message:
            # Add error message as optional parameter if supported
            self.add_optional_parameter(0x001D, error_message.encode('utf-8'))

        return self


class BindRequestPDU(RequestPDU):
    """
    Base class for bind request PDUs.

    Bind requests are used to establish SMPP sessions between clients and servers.
    """

    def __init__(
        self,
        system_id: str = '',
        password: str = '',
        system_type: str = '',
        interface_version: int = 0x34,
        addr_ton: int = 0,
        addr_npi: int = 0,
        address_range: str = '',
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.system_id = system_id
        self.password = password
        self.system_type = system_type
        self.interface_version = interface_version
        self.addr_ton = addr_ton
        self.addr_npi = addr_npi
        self.address_range = address_range

    def validate(self) -> None:
        """
        Validate bind request fields.

        Raises:
            SMPPPDUException: If validation fails
        """
        super().validate()

        # Validate required fields
        if not self.system_id:
            raise SMPPPDUException('system_id cannot be empty')
        if len(self.system_id) >= 16:
            raise SMPPPDUException(f'system_id too long: {len(self.system_id)} >= 16')
        if len(self.password) >= 9:
            raise SMPPPDUException(f'password too long: {len(self.password)} >= 9')
        if len(self.system_type) >= 13:
            raise SMPPPDUException(
                f'system_type too long: {len(self.system_type)} >= 13'
            )
        if self.interface_version not in (0x33, 0x34):
            raise SMPPPDUException(
                f'unsupported interface_version: 0x{self.interface_version:02X}'
            )
        if not (0 <= self.addr_ton <= 255):
            raise SMPPPDUException(f'invalid addr_ton: {self.addr_ton}')
        if not (0 <= self.addr_npi <= 255):
            raise SMPPPDUException(f'invalid addr_npi: {self.addr_npi}')
        if len(self.address_range) >= 41:
            raise SMPPPDUException(
                f'address_range too long: {len(self.address_range)} >= 41'
            )


class BindResponsePDU(ResponsePDU):
    """
    Base class for bind response PDUs.

    Bind responses are sent by servers in response to bind requests.
    """

    def __init__(self, system_id: str = '', **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.system_id = system_id

    def validate(self) -> None:
        """
        Validate bind response fields.

        Raises:
            SMPPPDUException: If validation fails
        """
        super().validate()

        if len(self.system_id) >= 16:
            raise SMPPPDUException(f'system_id too long: {len(self.system_id)} >= 16')


class MessagePDU(PDU):
    """
    Base class for message-related PDUs.

    Message PDUs handle SMS message transmission and delivery.
    """

    def __init__(
        self,
        service_type: str = '',
        source_addr_ton: int = 0,
        source_addr_npi: int = 0,
        source_addr: str = '',
        dest_addr_ton: int = 0,
        dest_addr_npi: int = 0,
        destination_addr: str = '',
        esm_class: int = 0,
        protocol_id: int = 0,
        priority_flag: int = 0,
        schedule_delivery_time: str = '',
        validity_period: str = '',
        registered_delivery: int = 0,
        replace_if_present_flag: int = 0,
        data_coding: int = 0,
        sm_default_msg_id: int = 0,
        short_message: bytes = b'',
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.service_type = service_type
        self.source_addr_ton = source_addr_ton
        self.source_addr_npi = source_addr_npi
        self.source_addr = source_addr
        self.dest_addr_ton = dest_addr_ton
        self.dest_addr_npi = dest_addr_npi
        self.destination_addr = destination_addr
        self.esm_class = esm_class
        self.protocol_id = protocol_id
        self.priority_flag = priority_flag
        self.schedule_delivery_time = schedule_delivery_time
        self.validity_period = validity_period
        self.registered_delivery = registered_delivery
        self.replace_if_present_flag = replace_if_present_flag
        self.data_coding = data_coding
        self.sm_default_msg_id = sm_default_msg_id
        self.short_message = short_message

    def validate(self) -> None:
        """
        Validate message PDU fields.

        Raises:
            SMPPPDUException: If validation fails
        """
        super().validate()

        from ..constants import (
            MAX_ADDRESS_LENGTH,
            MAX_SERVICE_TYPE_LENGTH,
            MAX_SHORT_MESSAGE_LENGTH,
        )

        # Length validations
        if len(self.service_type) > MAX_SERVICE_TYPE_LENGTH:
            raise SMPPPDUException(
                f'service_type too long: {len(self.service_type)} > {MAX_SERVICE_TYPE_LENGTH}'
            )
        if len(self.source_addr) > MAX_ADDRESS_LENGTH:
            raise SMPPPDUException(
                f'source_addr too long: {len(self.source_addr)} > {MAX_ADDRESS_LENGTH}'
            )
        if len(self.destination_addr) > MAX_ADDRESS_LENGTH:
            raise SMPPPDUException(
                f'destination_addr too long: {len(self.destination_addr)} > {MAX_ADDRESS_LENGTH}'
            )
        if len(self.short_message) > MAX_SHORT_MESSAGE_LENGTH:
            raise SMPPPDUException(
                f'short_message too long: {len(self.short_message)} > {MAX_SHORT_MESSAGE_LENGTH}'
            )

        # Range validations
        if not (0 <= self.source_addr_ton <= 255):
            raise SMPPPDUException(f'invalid source_addr_ton: {self.source_addr_ton}')
        if not (0 <= self.source_addr_npi <= 255):
            raise SMPPPDUException(f'invalid source_addr_npi: {self.source_addr_npi}')
        if not (0 <= self.dest_addr_ton <= 255):
            raise SMPPPDUException(f'invalid dest_addr_ton: {self.dest_addr_ton}')
        if not (0 <= self.dest_addr_npi <= 255):
            raise SMPPPDUException(f'invalid dest_addr_npi: {self.dest_addr_npi}')
        if not (0 <= self.esm_class <= 255):
            raise SMPPPDUException(f'invalid esm_class: {self.esm_class}')
        if not (0 <= self.protocol_id <= 255):
            raise SMPPPDUException(f'invalid protocol_id: {self.protocol_id}')
        if not (0 <= self.priority_flag <= 3):
            raise SMPPPDUException(f'invalid priority_flag: {self.priority_flag}')
        if not (0 <= self.registered_delivery <= 255):
            raise SMPPPDUException(
                f'invalid registered_delivery: {self.registered_delivery}'
            )
        if not (0 <= self.replace_if_present_flag <= 1):
            raise SMPPPDUException(
                f'invalid replace_if_present_flag: {self.replace_if_present_flag}'
            )
        if not (0 <= self.data_coding <= 255):
            raise SMPPPDUException(f'invalid data_coding: {self.data_coding}')
        if not (0 <= self.sm_default_msg_id <= 255):
            raise SMPPPDUException(
                f'invalid sm_default_msg_id: {self.sm_default_msg_id}'
            )


class EmptyBodyPDU(PDU):
    """
    Base class for PDUs with empty body.

    Some SMPP PDUs like enquire_link and enquire_link_resp have no body content.
    """

    def encode_body(self) -> bytes:
        """
        Encode empty body.

        Returns:
            Empty bytes
        """
        return b''

    def decode_body(self, data: bytes, offset: int = 0) -> int:
        """
        Decode empty body.

        Args:
            data: The byte data (unused)
            offset: Current offset

        Returns:
            The same offset (no data consumed)
        """
        return offset
