"""
Unit tests for SMPP Protocol Codec utilities.

Tests all encoding/decoding functions in src/smpp/protocol/codec.py including
C-string handling, integer packing, field validation, message encoding/decoding,
TLV parameter packing/unpacking, and PDU length calculation.
"""

import pytest
import struct
from smpp.protocol import codec
from smpp.protocol.constants import DataCoding
from smpp.exceptions import SMPPPDUException


class TestCStringEncoding:
    """Tests for encode_cstring function."""

    def test_encode_simple_string(self):
        """Test encoding a simple ASCII string."""
        result = codec.encode_cstring('hello', 10)
        assert result == b'hello\x00'

    def test_encode_empty_string(self):
        """Test encoding an empty string."""
        result = codec.encode_cstring('', 5)
        assert result == b'\x00'

    def test_encode_max_length_string(self):
        """Test encoding a string that exactly fits the limit."""
        result = codec.encode_cstring('test', 5)  # 4 chars + null = 5 bytes
        assert result == b'test\x00'

    def test_encode_string_too_long(self):
        """Test encoding a string that exceeds the maximum length."""
        with pytest.raises(SMPPPDUException, match='String too long'):
            codec.encode_cstring('toolong', 5)

    def test_encode_custom_encoding(self):
        """Test encoding with custom character encoding."""
        result = codec.encode_cstring('café', 10, encoding='utf-8')
        assert result == b'caf\xc3\xa9\x00'

    def test_encode_encoding_error(self):
        """Test encoding with unsupported characters."""
        with pytest.raises(SMPPPDUException, match='String encoding error'):
            codec.encode_cstring('café', 10, encoding='ascii')

    def test_encode_multibyte_too_long(self):
        """Test when encoded bytes exceed limit even if string length is OK."""
        # 4 chars but 6 bytes when encoded in UTF-8, need space for null terminator
        with pytest.raises(SMPPPDUException, match='Encoded string too long'):
            codec.encode_cstring('café', 5, encoding='utf-8')


class TestCStringDecoding:
    """Tests for decode_cstring function."""

    def test_decode_simple_string(self):
        """Test decoding a simple null-terminated string."""
        data = b'hello\x00world'
        result, new_offset = codec.decode_cstring(data, 0, 10)
        assert result == 'hello'
        assert new_offset == 6

    def test_decode_empty_string(self):
        """Test decoding an empty string."""
        data = b'\x00remaining'
        result, new_offset = codec.decode_cstring(data, 0, 5)
        assert result == ''
        assert new_offset == 1

    def test_decode_at_offset(self):
        """Test decoding starting from a specific offset."""
        data = b'prefixtest\x00suffix'
        result, new_offset = codec.decode_cstring(data, 6, 10)
        assert result == 'test'
        assert new_offset == 11

    def test_decode_insufficient_data(self):
        """Test decoding when offset is beyond data length."""
        data = b'short'
        with pytest.raises(
            SMPPPDUException, match='Insufficient data for string field'
        ):
            codec.decode_cstring(data, 10, 5)

    def test_decode_not_null_terminated(self):
        """Test decoding when string is not null-terminated within max_length."""
        data = b'noterminator'
        with pytest.raises(SMPPPDUException, match='String not null-terminated within'):
            codec.decode_cstring(data, 0, 5)

    def test_decode_custom_encoding(self):
        """Test decoding with custom character encoding."""
        data = b'caf\xc3\xa9\x00'
        result, new_offset = codec.decode_cstring(data, 0, 10, encoding='utf-8')
        assert result == 'café'
        assert new_offset == 6

    def test_decode_encoding_error(self):
        """Test decoding with invalid byte sequence."""
        data = b'\xff\xfe\x00'  # Invalid UTF-8
        with pytest.raises(SMPPPDUException, match='String decoding error'):
            codec.decode_cstring(data, 0, 10, encoding='utf-8')


class TestIntegerEncoding:
    """Tests for encode_integer function."""

    def test_encode_1_byte_unsigned(self):
        """Test encoding 1-byte unsigned integer."""
        result = codec.encode_integer(255, 1)
        assert result == b'\xff'

    def test_encode_1_byte_signed(self):
        """Test encoding 1-byte signed integer."""
        result = codec.encode_integer(-1, 1, signed=True)
        assert result == b'\xff'

    def test_encode_2_byte_unsigned(self):
        """Test encoding 2-byte unsigned integer."""
        result = codec.encode_integer(0x1234, 2)
        assert result == b'\x12\x34'

    def test_encode_4_byte_unsigned(self):
        """Test encoding 4-byte unsigned integer."""
        result = codec.encode_integer(0x12345678, 4)
        assert result == b'\x12\x34\x56\x78'

    def test_encode_8_byte_unsigned(self):
        """Test encoding 8-byte unsigned integer."""
        result = codec.encode_integer(0x123456789ABCDEF0, 8)
        assert result == b'\x12\x34\x56\x78\x9a\xbc\xde\xf0'

    def test_encode_invalid_size(self):
        """Test encoding with invalid size."""
        with pytest.raises(SMPPPDUException, match='Invalid integer size'):
            codec.encode_integer(123, 3)

    def test_encode_value_out_of_range(self):
        """Test encoding value that's out of range for the size."""
        with pytest.raises(SMPPPDUException, match='Integer encoding error'):
            codec.encode_integer(256, 1)  # Too big for 1 byte


class TestIntegerDecoding:
    """Tests for decode_integer function."""

    def test_decode_1_byte_unsigned(self):
        """Test decoding 1-byte unsigned integer."""
        data = b'\xff\x00'
        result, new_offset = codec.decode_integer(data, 0, 1)
        assert result == 255
        assert new_offset == 1

    def test_decode_1_byte_signed(self):
        """Test decoding 1-byte signed integer."""
        data = b'\xff\x00'
        result, new_offset = codec.decode_integer(data, 0, 1, signed=True)
        assert result == -1
        assert new_offset == 1

    def test_decode_2_byte_unsigned(self):
        """Test decoding 2-byte unsigned integer."""
        data = b'\x12\x34\x56'
        result, new_offset = codec.decode_integer(data, 0, 2)
        assert result == 0x1234
        assert new_offset == 2

    def test_decode_4_byte_unsigned(self):
        """Test decoding 4-byte unsigned integer."""
        data = b'\x12\x34\x56\x78\x90'
        result, new_offset = codec.decode_integer(data, 0, 4)
        assert result == 0x12345678
        assert new_offset == 4

    def test_decode_at_offset(self):
        """Test decoding starting from a specific offset."""
        data = b'\x00\x00\x12\x34'
        result, new_offset = codec.decode_integer(data, 2, 2)
        assert result == 0x1234
        assert new_offset == 4

    def test_decode_insufficient_data(self):
        """Test decoding when there's insufficient data."""
        data = b'\x12'
        with pytest.raises(
            SMPPPDUException, match='Insufficient data for 2-byte integer'
        ):
            codec.decode_integer(data, 0, 2)

    def test_decode_invalid_size(self):
        """Test decoding with invalid size."""
        data = b'\x12\x34\x56'
        with pytest.raises(SMPPPDUException, match='Invalid integer size'):
            codec.decode_integer(data, 0, 3)


class TestFieldValidation:
    """Tests for validate_field_length function."""

    def test_validate_valid_string(self):
        """Test validation of a valid string field."""
        # Should not raise any exception
        codec.validate_field_length('test_field', 'hello', 0, 10)

    def test_validate_valid_bytes(self):
        """Test validation of a valid bytes field."""
        # Should not raise any exception
        codec.validate_field_length('test_field', b'hello', 0, 10)

    def test_validate_too_short(self):
        """Test validation of field that's too short."""
        with pytest.raises(SMPPPDUException, match='test_field too short'):
            codec.validate_field_length('test_field', 'hi', 5, 10)

    def test_validate_too_long(self):
        """Test validation of field that's too long."""
        with pytest.raises(SMPPPDUException, match='test_field too long'):
            codec.validate_field_length('test_field', 'verylongstring', 0, 5)

    def test_validate_no_max_length(self):
        """Test validation when no maximum length is specified."""
        # Should not raise any exception
        codec.validate_field_length('test_field', 'verylongstring', 0, None)

    def test_validate_exact_min_length(self):
        """Test validation when field is exactly at minimum length."""
        # Should not raise any exception
        codec.validate_field_length('test_field', 'hello', 5, 10)

    def test_validate_exact_max_length(self):
        """Test validation when field is exactly at maximum length."""
        # Should not raise any exception
        codec.validate_field_length('test_field', 'hello', 0, 5)


class TestMessageEncoding:
    """Tests for encode_message_with_encoding function."""

    def test_encode_default_coding(self):
        """Test encoding with default data coding."""
        result = codec.encode_message_with_encoding('hello', DataCoding.DEFAULT)
        assert result == b'hello'

    def test_encode_ascii(self):
        """Test encoding with ASCII data coding."""
        result = codec.encode_message_with_encoding('hello', DataCoding.IA5_ASCII)
        assert result == b'hello'

    def test_encode_latin1(self):
        """Test encoding with Latin-1 data coding."""
        result = codec.encode_message_with_encoding('café', DataCoding.LATIN_1)
        assert result == b'caf\xe9'

    def test_encode_ucs2(self):
        """Test encoding with UCS2 data coding."""
        result = codec.encode_message_with_encoding('hello', DataCoding.UCS2)
        assert result == b'\x00h\x00e\x00l\x00l\x00o'

    def test_encode_octet_unspecified(self):
        """Test encoding with octet unspecified data coding."""
        result = codec.encode_message_with_encoding(
            'hello', DataCoding.OCTET_UNSPECIFIED_1
        )
        assert result == b'hello'

    def test_encode_unknown_coding(self):
        """Test encoding with unknown data coding (should fallback to UTF-8)."""
        result = codec.encode_message_with_encoding('hello', 99)
        assert result == b'hello'

    def test_encode_unicode_with_utf8_fallback(self):
        """Test encoding Unicode with UTF-8 fallback."""
        result = codec.encode_message_with_encoding('🙂', 99)  # Unknown coding
        assert result == b'\xf0\x9f\x99\x82'

    def test_encode_error(self):
        """Test encoding error handling."""
        with pytest.raises(SMPPPDUException, match='Message encoding error'):
            codec.encode_message_with_encoding('café', DataCoding.IA5_ASCII)


class TestMessageDecoding:
    """Tests for decode_message_with_encoding function."""

    def test_decode_default_coding(self):
        """Test decoding with default data coding."""
        result = codec.decode_message_with_encoding(b'hello', DataCoding.DEFAULT)
        assert result == 'hello'

    def test_decode_ascii(self):
        """Test decoding with ASCII data coding."""
        result = codec.decode_message_with_encoding(b'hello', DataCoding.IA5_ASCII)
        assert result == 'hello'

    def test_decode_latin1(self):
        """Test decoding with Latin-1 data coding."""
        result = codec.decode_message_with_encoding(b'caf\xe9', DataCoding.LATIN_1)
        assert result == 'café'

    def test_decode_ucs2(self):
        """Test decoding with UCS2 data coding."""
        result = codec.decode_message_with_encoding(
            b'\x00h\x00e\x00l\x00l\x00o', DataCoding.UCS2
        )
        assert result == 'hello'

    def test_decode_octet_unspecified(self):
        """Test decoding with octet unspecified data coding."""
        result = codec.decode_message_with_encoding(
            b'hello', DataCoding.OCTET_UNSPECIFIED_1
        )
        assert result == 'hello'

    def test_decode_unknown_coding(self):
        """Test decoding with unknown data coding (should fallback to UTF-8)."""
        result = codec.decode_message_with_encoding(b'hello', 99)
        assert result == 'hello'

    def test_decode_unicode_with_utf8_fallback(self):
        """Test decoding Unicode with UTF-8 fallback."""
        result = codec.decode_message_with_encoding(b'\xf0\x9f\x99\x82', 99)
        assert result == '🙂'

    def test_decode_error_with_replacement(self):
        """Test decoding with invalid bytes (should use replacement chars)."""
        # Invalid UTF-8 with unknown data coding - should use error='replace'
        result = codec.decode_message_with_encoding(b'\xff\xfe', 99)
        assert '\ufffd' in result  # Replacement character

    def test_decode_error_with_known_coding(self):
        """Test decoding error with known data coding."""
        with pytest.raises(SMPPPDUException, match='Message decoding error'):
            codec.decode_message_with_encoding(b'\xff\xfe', DataCoding.IA5_ASCII)


class TestTLVPacking:
    """Tests for pack_tlv_parameter function."""

    def test_pack_simple_tlv(self):
        """Test packing a simple TLV parameter."""
        result = codec.pack_tlv_parameter(0x1234, b'value')
        expected = struct.pack('>HH', 0x1234, 5) + b'value'
        assert result == expected

    def test_pack_empty_value(self):
        """Test packing TLV with empty value."""
        result = codec.pack_tlv_parameter(0x1234, b'')
        expected = struct.pack('>HH', 0x1234, 0)
        assert result == expected

    def test_pack_max_tag(self):
        """Test packing TLV with maximum tag value."""
        result = codec.pack_tlv_parameter(0xFFFF, b'test')
        expected = struct.pack('>HH', 0xFFFF, 4) + b'test'
        assert result == expected

    def test_pack_invalid_tag_negative(self):
        """Test packing TLV with invalid negative tag."""
        with pytest.raises(SMPPPDUException, match='Invalid TLV tag'):
            codec.pack_tlv_parameter(-1, b'value')

    def test_pack_invalid_tag_too_large(self):
        """Test packing TLV with tag too large."""
        with pytest.raises(SMPPPDUException, match='Invalid TLV tag'):
            codec.pack_tlv_parameter(0x10000, b'value')

    def test_pack_value_too_long(self):
        """Test packing TLV with value too long."""
        long_value = b'x' * 0x10000  # 65536 bytes
        with pytest.raises(SMPPPDUException, match='TLV value too long'):
            codec.pack_tlv_parameter(0x1234, long_value)


class TestTLVUnpacking:
    """Tests for unpack_tlv_parameter function."""

    def test_unpack_simple_tlv(self):
        """Test unpacking a simple TLV parameter."""
        data = struct.pack('>HH', 0x1234, 5) + b'value' + b'extra'
        tag, value, new_offset = codec.unpack_tlv_parameter(data, 0)
        assert tag == 0x1234
        assert value == b'value'
        assert new_offset == 9

    def test_unpack_empty_value(self):
        """Test unpacking TLV with empty value."""
        data = struct.pack('>HH', 0x1234, 0) + b'remaining'
        tag, value, new_offset = codec.unpack_tlv_parameter(data, 0)
        assert tag == 0x1234
        assert value == b''
        assert new_offset == 4

    def test_unpack_at_offset(self):
        """Test unpacking TLV starting from a specific offset."""
        prefix = b'prefix'
        tlv_data = struct.pack('>HH', 0x5678, 4) + b'test'
        data = prefix + tlv_data + b'suffix'
        tag, value, new_offset = codec.unpack_tlv_parameter(data, 6)
        assert tag == 0x5678
        assert value == b'test'
        assert new_offset == 14  # 6 (prefix) + 4 (header) + 4 (value) = 14

    def test_unpack_insufficient_header_data(self):
        """Test unpacking when there's insufficient data for header."""
        data = b'\x12\x34\x00'  # Only 3 bytes, need 4 for header
        with pytest.raises(SMPPPDUException, match='Insufficient data for TLV header'):
            codec.unpack_tlv_parameter(data, 0)

    def test_unpack_insufficient_value_data(self):
        """Test unpacking when there's insufficient data for value."""
        data = struct.pack('>HH', 0x1234, 10) + b'short'  # Says 10 bytes but only 5
        with pytest.raises(SMPPPDUException, match='Insufficient data for TLV value'):
            codec.unpack_tlv_parameter(data, 0)

    def test_unpack_at_end_of_data(self):
        """Test unpacking when offset is at the end of data."""
        data = b'test'
        with pytest.raises(SMPPPDUException, match='Insufficient data for TLV header'):
            codec.unpack_tlv_parameter(data, 4)


class TestPDULengthCalculation:
    """Tests for calculate_pdu_length function."""

    def test_calculate_basic_length(self):
        """Test calculating basic PDU length."""
        result = codec.calculate_pdu_length(16, 100, 20)
        assert result == 136

    def test_calculate_no_optional_params(self):
        """Test calculating PDU length without optional parameters."""
        result = codec.calculate_pdu_length(16, 100)
        assert result == 116

    def test_calculate_zero_body(self):
        """Test calculating PDU length with zero body size."""
        result = codec.calculate_pdu_length(16, 0, 10)
        assert result == 26

    def test_calculate_maximum_allowed(self):
        """Test calculating maximum allowed PDU length."""
        result = codec.calculate_pdu_length(16, 65520)  # Just under limit
        assert result == 65536

    def test_calculate_exceeds_maximum(self):
        """Test calculating PDU length that exceeds maximum."""
        with pytest.raises(SMPPPDUException, match='PDU too large'):
            codec.calculate_pdu_length(16, 65521)  # Over limit

    def test_calculate_large_optional_params(self):
        """Test calculating PDU length with large optional parameters."""
        with pytest.raises(SMPPPDUException, match='PDU too large'):
            codec.calculate_pdu_length(16, 32768, 32768)  # Total > 65536


class TestRoundTripOperations:
    """Tests for round-trip encoding/decoding operations."""

    def test_cstring_roundtrip(self):
        """Test encoding and decoding C-strings."""
        original = 'hello world'
        encoded = codec.encode_cstring(original, 20)
        decoded, _ = codec.decode_cstring(encoded, 0, 20)
        assert decoded == original

    def test_integer_roundtrip(self):
        """Test encoding and decoding integers."""
        original = 0x12345678
        encoded = codec.encode_integer(original, 4)
        decoded, _ = codec.decode_integer(encoded, 0, 4)
        assert decoded == original

    def test_message_roundtrip_utf8(self):
        """Test encoding and decoding messages with UTF-8."""
        original = 'Hello 🌍'
        encoded = codec.encode_message_with_encoding(
            original, DataCoding.OCTET_UNSPECIFIED_1
        )
        decoded = codec.decode_message_with_encoding(
            encoded, DataCoding.OCTET_UNSPECIFIED_1
        )
        assert decoded == original

    def test_message_roundtrip_ucs2(self):
        """Test encoding and decoding messages with UCS2."""
        original = 'Hello 🌍'
        encoded = codec.encode_message_with_encoding(original, DataCoding.UCS2)
        decoded = codec.decode_message_with_encoding(encoded, DataCoding.UCS2)
        assert decoded == original

    def test_tlv_roundtrip(self):
        """Test packing and unpacking TLV parameters."""
        original_tag = 0x1234
        original_value = b'test value'
        packed = codec.pack_tlv_parameter(original_tag, original_value)
        unpacked_tag, unpacked_value, _ = codec.unpack_tlv_parameter(packed, 0)
        assert unpacked_tag == original_tag
        assert unpacked_value == original_value


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_max_values(self):
        """Test handling of maximum values."""
        # Test maximum TLV tag
        result = codec.pack_tlv_parameter(0xFFFF, b'')
        assert len(result) == 4

        # Test maximum valid PDU length
        length = codec.calculate_pdu_length(0, 65536)
        assert length == 65536

    def test_zero_values(self):
        """Test handling of zero values."""
        # Zero-length string
        result = codec.encode_cstring('', 1)
        assert result == b'\x00'

        # Zero tag
        result = codec.pack_tlv_parameter(0, b'test')
        assert len(result) == 8

        # Zero integer
        result = codec.encode_integer(0, 4)
        assert result == b'\x00\x00\x00\x00'

    def test_boundary_lengths(self):
        """Test boundary length conditions."""
        # String exactly at max length (including null terminator)
        codec.encode_cstring('test', 5)  # Should work

        # Field validation at exact boundaries
        codec.validate_field_length('test', 'hello', 5, 5)  # Should work
