"""
Unit tests for GSM functionality.
"""

import pytest
from smpp.gsm import encode_gsm7, decode_gsm7, make_parts, UDH, ConcatenatedSMSHeader
from smpp.gsm.encoding import GSM_7BIT_BASIC, GSM_7BIT_EXTENDED
from smpp.protocol.pdu.message import SubmitSm


class TestGSM7BitEncoding:
    """Test GSM 7-bit encoding and decoding."""

    def test_basic_encoding(self):
        """Test basic GSM 7-bit encoding."""
        text = 'Hello World'
        encoded, char_count = encode_gsm7(text)
        decoded = decode_gsm7(encoded, char_count)

        assert decoded == text
        assert char_count == len(text)

    def test_extended_characters(self):
        """Test GSM 7-bit extended characters."""
        text = 'Hello {World} €'
        encoded, char_count = encode_gsm7(text)
        decoded = decode_gsm7(encoded, char_count)

        assert decoded == text
        assert char_count == 18  # 15 chars - 3 extended + (3 * 2) = 18

    def test_empty_string(self):
        """Test encoding empty string."""
        encoded, char_count = encode_gsm7('')
        decoded = decode_gsm7(encoded, char_count)

        assert decoded == ''
        assert char_count == 0
        assert encoded == b''

    def test_gsm_basic_charset(self):
        """Test all basic GSM characters."""
        text = '@£$¥èéùìòÇ\nØø\rÅåΔ_ΦΓΛΩΠΨΣΘΞ'
        encoded, char_count = encode_gsm7(text)
        decoded = decode_gsm7(encoded, char_count)

        assert decoded == text
        assert char_count == len(text)

    def test_invalid_character(self):
        """Test encoding invalid character."""
        with pytest.raises(ValueError, match='not supported in GSM 7-bit charset'):
            encode_gsm7('Hello 中文')


class TestGSM0338Codec:
    """Test the unpacked 'gsm0338' codec used for data_coding 0."""

    def test_round_trip_basic_table(self):
        text = GSM_7BIT_BASIC.replace('\x1b', '')
        encoded = text.encode('gsm0338')
        assert encoded == bytes(i for i in range(128) if i != 0x1B)
        assert encoded.decode('gsm0338') == text

    def test_round_trip_extension_table(self):
        text = ''.join(GSM_7BIT_EXTENDED)
        encoded = text.encode('gsm0338')
        assert encoded == b''.join(bytes([0x1B, v]) for v in GSM_7BIT_EXTENDED.values())
        assert encoded.decode('gsm0338') == text

    def test_unpacked_bytes(self):
        assert '@_€{'.encode('gsm0338') == b'\x00\x11\x1b\x65\x1b\x28'

    @pytest.mark.parametrize('text', ['ж', '\x1b'])
    def test_encode_rejects(self, text):
        with pytest.raises(UnicodeEncodeError):
            text.encode('gsm0338')

    def test_encode_replace(self):
        assert 'жa'.encode('gsm0338', errors='replace') == b'?a'

    def test_decode_rejects_high_byte(self):
        with pytest.raises(UnicodeDecodeError):
            b'\x80'.decode('gsm0338')
        assert b'A\x80'.decode('gsm0338', errors='replace') == 'A\ufffd'

    def test_decode_escape_edge_cases(self):
        assert b'A\x1b'.decode('gsm0338') == 'A '  # trailing ESC
        assert b'\x1b\x1bA'.decode('gsm0338') == ' A'  # reserved ESC ESC
        assert b'\x1bA'.decode('gsm0338') == 'A'  # unknown escape -> basic char


class TestUDH:
    """Test UDH handling."""

    def test_concatenated_sms_8bit(self):
        """Test 8-bit concatenated SMS UDH."""
        header = ConcatenatedSMSHeader(
            reference=123, total_parts=3, part_number=1, use_16bit_ref=False
        )

        element = header.to_udh_element()
        assert element.iei == UDH.IEI_CONCATENATED_SMS_8BIT
        assert len(element.data) == 3

        # Test round trip
        parsed_header = ConcatenatedSMSHeader.from_udh_element(element)
        assert parsed_header.reference == 123
        assert parsed_header.total_parts == 3
        assert parsed_header.part_number == 1
        assert not parsed_header.use_16bit_ref

    def test_concatenated_sms_16bit(self):
        """Test 16-bit concatenated SMS UDH."""
        header = ConcatenatedSMSHeader(
            reference=12345, total_parts=5, part_number=2, use_16bit_ref=True
        )

        element = header.to_udh_element()
        assert element.iei == UDH.IEI_CONCATENATED_SMS_16BIT
        assert len(element.data) == 4

        # Test round trip
        parsed_header = ConcatenatedSMSHeader.from_udh_element(element)
        assert parsed_header.reference == 12345
        assert parsed_header.total_parts == 5
        assert parsed_header.part_number == 2
        assert parsed_header.use_16bit_ref

    def test_udh_encoding_decoding(self):
        """Test UDH encoding and decoding."""
        # Create UDH with concatenated SMS element
        concat_header = ConcatenatedSMSHeader(
            reference=255, total_parts=2, part_number=1, use_16bit_ref=False
        )

        udh = UDH([concat_header.to_udh_element()])
        encoded = udh.encode()

        # Decode UDH
        decoded_udh, offset = UDH.decode(encoded)

        assert len(decoded_udh.elements) == 1
        element = decoded_udh.elements[0]
        assert element.iei == UDH.IEI_CONCATENATED_SMS_8BIT

        # Verify concatenated info
        parsed_header = ConcatenatedSMSHeader.from_udh_element(element)
        assert parsed_header.reference == 255
        assert parsed_header.total_parts == 2
        assert parsed_header.part_number == 1


class TestMessageSegmentation:
    """Test message segmentation."""

    def test_single_part_message(self):
        """Test message that fits in single SMS."""
        message = 'Hello World'
        parts = make_parts(message, encoding='gsm7')

        assert len(parts) == 1
        part = parts[0]
        assert part.part_number == 1
        assert part.total_parts == 1
        assert part.udh is None
        assert part.encoding == 0  # GSM 7-bit

    def test_multi_part_gsm7_message(self):
        """Test GSM 7-bit message requiring multiple parts."""
        # Create message longer than 160 characters
        message = 'This is a test message. ' * 10  # 240 characters
        parts = make_parts(message, encoding='gsm7')

        assert len(parts) == 2  # Should split into 2 parts

        # Check first part
        assert parts[0].part_number == 1
        assert parts[0].total_parts == 2
        assert parts[0].udh is not None
        assert parts[0].reference is not None

        # Check second part
        assert parts[1].part_number == 2
        assert parts[1].total_parts == 2
        assert parts[1].udh is not None
        assert parts[1].reference == parts[0].reference

        # Check UDH has concatenated SMS info
        concat_info = parts[0].get_concatenated_info()
        assert concat_info is not None
        assert concat_info.total_parts == 2
        assert concat_info.part_number == 1

    def test_multi_part_binary_message(self):
        """Test binary message requiring multiple parts."""
        # Create message longer than 140 bytes
        message = b'X' * 200
        parts = make_parts(message, encoding='latin1')

        assert len(parts) == 2  # Should split into 2 parts
        assert all(part.udh is not None for part in parts)
        assert all(part.total_parts == 2 for part in parts)

    def test_utf16_encoding(self):
        """Test UTF-16 encoding segmentation."""
        message = 'Hello 世界 ' * 20  # Unicode message
        parts = make_parts(message, encoding='utf16')

        assert len(parts) >= 1
        assert parts[0].encoding == 8  # UTF-16 data coding


class TestMessagePDUIntegration:
    """Test integration with MessagePDU."""

    def test_submit_sm_with_udh(self):
        """Test SubmitSm PDU with UDH."""
        # Create segmented message
        message = 'Long message ' * 20
        parts = make_parts(message, encoding='gsm7')

        assert len(parts) > 1
        part = parts[0]

        # Create SubmitSm with UDH
        pdu = SubmitSm(
            source_addr='1234',
            destination_addr='5678',
            short_message=part.get_short_message(),
            esm_class=part.get_esm_class(),
            data_coding=part.encoding,
        )

        # Test UDH detection
        assert pdu.has_udh()
        assert pdu.is_concatenated_sms()

        # Test UDH extraction
        udh = pdu.get_udh()
        assert udh is not None

        # Test concatenated info
        concat_info = pdu.get_concatenated_info()
        assert concat_info is not None
        assert concat_info.part_number == 1
        assert concat_info.total_parts > 1

        # Test message content extraction
        content = pdu.get_message_content()
        assert len(content) < len(pdu.short_message)  # Should be shorter without UDH

    def test_submit_sm_without_udh(self):
        """Test SubmitSm PDU without UDH."""
        pdu = SubmitSm(
            source_addr='1234',
            destination_addr='5678',
            short_message=b'Hello World',
            esm_class=0,
            data_coding=0,
        )

        assert not pdu.has_udh()
        assert not pdu.is_concatenated_sms()
        assert pdu.get_udh() is None
        assert pdu.get_concatenated_info() is None
        assert pdu.get_message_content() == b'Hello World'
