"""
SMPP Protocol Codec Utilities

This module provides encoding and decoding utilities for SMPP protocol fields,
including C-string handling, integer packing, and field validation.
"""

import struct
import typing as tp

from .. import gsm  # noqa: F401  registers the 'gsm0338' codec
from ..exceptions import SMPPPDUException


def encode_cstring(s: str, max_length: int, encoding: str = 'latin-1') -> bytes:
    """
    Encode a string as a C-style null-terminated string with length validation.

    Args:
        s: String to encode
        max_length: Maximum allowed length including null terminator
        encoding: Character encoding to use

    Returns:
        Encoded bytes with null terminator

    Raises:
        SMPPPDUException: If string is too long or encoding fails
    """
    if len(s) >= max_length:
        raise SMPPPDUException(
            f'String too long: {len(s)} chars, max {max_length - 1} allowed'
        )

    try:
        encoded = s.encode(encoding)
        if len(encoded) >= max_length:
            raise SMPPPDUException(
                f'Encoded string too long: {len(encoded)} bytes, max {max_length - 1} allowed'
            )
        return encoded + b'\x00'
    except UnicodeEncodeError as e:
        raise SMPPPDUException(f'String encoding error: {e}') from e


def decode_cstring(
    data: bytes, offset: int, max_length: int, encoding: str = 'latin-1'
) -> tp.Tuple[str, int]:
    """
    Decode a C-style null-terminated string from bytes.

    Args:
        data: Byte data to decode from
        offset: Starting offset in data
        max_length: Maximum field length to search
        encoding: Character encoding to use

    Returns:
        Tuple of (decoded_string, new_offset)

    Raises:
        SMPPPDUException: If string is not properly terminated or decoding fails
    """
    if offset >= len(data):
        raise SMPPPDUException('Insufficient data for string field')

    # Find null terminator within max_length
    end_offset = offset
    search_limit = min(len(data), offset + max_length)

    while end_offset < search_limit and data[end_offset] != 0:
        end_offset += 1

    if end_offset >= search_limit:
        raise SMPPPDUException(f'String not null-terminated within {max_length} bytes')

    if end_offset >= len(data) or data[end_offset] != 0:
        raise SMPPPDUException('String not properly null-terminated')

    try:
        decoded = data[offset:end_offset].decode(encoding)
        return decoded, end_offset + 1
    except UnicodeDecodeError as e:
        raise SMPPPDUException(f'String decoding error: {e}') from e


def encode_integer(value: int, size: int, signed: bool = False) -> bytes:
    """
    Encode an integer to bytes with specified size.

    Args:
        value: Integer value to encode
        size: Size in bytes (1, 2, 4, or 8)
        signed: Whether the integer is signed

    Returns:
        Encoded bytes in big-endian format

    Raises:
        SMPPPDUException: If value is out of range or invalid size
    """
    format_map = {
        1: 'b' if signed else 'B',
        2: 'h' if signed else 'H',
        4: 'i' if signed else 'I',
        8: 'q' if signed else 'Q',
    }

    if size not in format_map:
        raise SMPPPDUException(f'Invalid integer size: {size}')

    format_char = '>' + format_map[size]  # Big-endian

    try:
        return struct.pack(format_char, value)
    except struct.error as e:
        raise SMPPPDUException(f'Integer encoding error: {e}') from e


def decode_integer(
    data: bytes, offset: int, size: int, signed: bool = False
) -> tp.Tuple[int, int]:
    """
    Decode an integer from bytes.

    Args:
        data: Byte data to decode from
        offset: Starting offset in data
        size: Size in bytes (1, 2, 4, or 8)
        signed: Whether the integer is signed

    Returns:
        Tuple of (decoded_integer, new_offset)

    Raises:
        SMPPPDUException: If insufficient data or invalid size
    """
    if offset + size > len(data):
        raise SMPPPDUException(
            f'Insufficient data for {size}-byte integer at offset {offset}'
        )

    format_map = {
        1: 'b' if signed else 'B',
        2: 'h' if signed else 'H',
        4: 'i' if signed else 'I',
        8: 'q' if signed else 'Q',
    }

    if size not in format_map:
        raise SMPPPDUException(f'Invalid integer size: {size}')

    format_char = '>' + format_map[size]  # Big-endian

    try:
        value = struct.unpack(format_char, data[offset : offset + size])[0]
        return value, offset + size
    except struct.error as e:
        raise SMPPPDUException(f'Integer decoding error: {e}') from e


def validate_field_length(
    field_name: str,
    value: tp.Union[str, bytes],
    min_length: int = 0,
    max_length: tp.Optional[int] = None,
) -> None:
    """
    Validate that a field value meets length requirements.

    Args:
        field_name: Name of the field for error messages
        value: Field value to validate
        min_length: Minimum allowed length
        max_length: Maximum allowed length (None for no limit)

    Raises:
        SMPPPDUException: If field length is invalid
    """
    length = len(value)

    if length < min_length:
        raise SMPPPDUException(f'{field_name} too short: {length} < {min_length}')

    if max_length is not None and length > max_length:
        raise SMPPPDUException(f'{field_name} too long: {length} > {max_length}')


# SMPP v3.4 §5.2.19 data_coding -> Python codec. The only such map in smpp.
_DATA_CODING_CODECS = {
    0x00: 'gsm0338',  # SMSC default alphabet, GSM 03.38 unpacked
    0x01: 'ascii',
    0x02: 'utf-8',  # octet unspecified: the caller owns the bytes' meaning
    0x03: 'latin-1',
    0x04: 'utf-8',  # octet unspecified
    0x06: 'iso8859_5',
    0x07: 'iso8859_8',
    0x08: 'utf-16-be',
    0x0A: 'iso2022_jp',
}


def codec_for_data_coding(data_coding: int) -> str:
    """
    Return the Python codec name for an SMPP data_coding value.

    0xF0-0xF7 (GSM message class group) map to GSM 03.38 when bit 0x04 is
    clear and to 8-bit data otherwise. 0xF8-0xFF set the reserved bit 3 and
    are unsupported, matching validate_data_coding.

    Raises:
        SMPPPDUException: If the data coding is unsupported
    """
    if data_coding in _DATA_CODING_CODECS:
        return _DATA_CODING_CODECS[data_coding]
    if 0xF0 <= data_coding <= 0xF7:
        return 'utf-8' if data_coding & 0x04 else 'gsm0338'
    raise SMPPPDUException(f'Unsupported data_coding {data_coding:#04x}')


def encode_message_with_encoding(message: str, data_coding: int) -> bytes:
    """
    Encode a message using the specified data coding scheme.

    Args:
        message: Message text to encode
        data_coding: SMPP data coding value

    Returns:
        Encoded message bytes

    Raises:
        SMPPPDUException: If encoding fails or data coding is unsupported
    """
    try:
        return message.encode(codec_for_data_coding(data_coding))
    except UnicodeEncodeError as e:
        raise SMPPPDUException(f'Message encoding error: {e}') from e


def decode_message_with_encoding(message_bytes: bytes, data_coding: int) -> str:
    """
    Decode a message using the specified data coding scheme.

    Args:
        message_bytes: Encoded message bytes
        data_coding: SMPP data coding value

    Returns:
        Decoded message string

    Raises:
        SMPPPDUException: If decoding fails or data coding is unsupported
    """
    try:
        return message_bytes.decode(codec_for_data_coding(data_coding))
    except UnicodeDecodeError as e:
        raise SMPPPDUException(f'Message decoding error: {e}') from e


def pack_tlv_parameter(tag: int, value: bytes) -> bytes:
    """
    Pack a TLV (Tag-Length-Value) parameter.

    Args:
        tag: Parameter tag (16-bit)
        value: Parameter value bytes

    Returns:
        Packed TLV bytes

    Raises:
        SMPPPDUException: If tag or length is invalid
    """
    if not (0 <= tag <= 0xFFFF):
        raise SMPPPDUException(f'Invalid TLV tag: 0x{tag:04X}')

    length = len(value)
    if length > 0xFFFF:
        raise SMPPPDUException(f'TLV value too long: {length} bytes')

    try:
        return struct.pack('>HH', tag, length) + value
    except struct.error as e:
        raise SMPPPDUException(f'TLV packing error: {e}') from e


def unpack_tlv_parameter(data: bytes, offset: int = 0) -> tp.Tuple[int, bytes, int]:
    """
    Unpack a TLV (Tag-Length-Value) parameter.

    Args:
        data: Byte data containing TLV
        offset: Starting offset in data

    Returns:
        Tuple of (tag, value, new_offset)

    Raises:
        SMPPPDUException: If insufficient data or invalid format
    """
    if offset + 4 > len(data):
        raise SMPPPDUException('Insufficient data for TLV header')

    try:
        tag, length = struct.unpack('>HH', data[offset : offset + 4])
    except struct.error as e:
        raise SMPPPDUException(f'TLV header unpacking error: {e}') from e

    value_offset = offset + 4
    if value_offset + length > len(data):
        raise SMPPPDUException('Insufficient data for TLV value')

    value = data[value_offset : value_offset + length]
    return tag, value, value_offset + length


def calculate_pdu_length(
    header_size: int, body_size: int, optional_params_size: int = 0
) -> int:
    """
    Calculate total PDU length including header, body, and optional parameters.

    Args:
        header_size: Size of PDU header
        body_size: Size of PDU body
        optional_params_size: Size of optional parameters

    Returns:
        Total PDU length

    Raises:
        SMPPPDUException: If calculated length exceeds maximum
    """
    total_length = header_size + body_size + optional_params_size

    # Check against SMPP maximum PDU size
    MAX_PDU_SIZE = 65536
    if total_length > MAX_PDU_SIZE:
        raise SMPPPDUException(
            f'PDU too large: {total_length} bytes exceeds maximum {MAX_PDU_SIZE}'
        )

    return total_length
