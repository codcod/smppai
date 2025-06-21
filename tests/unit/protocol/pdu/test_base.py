"""Unit tests for SMPP PDU base classes."""

import pytest
import struct
from unittest.mock import patch

from smpp.exceptions import SMPPPDUException
from smpp.protocol.constants import CommandStatus
from smpp.protocol.pdu.base import TLVParameter, PDU, BindRequestPDU, MessagePDU


class TestTLVParameter:
    """Test TLVParameter class."""

    def test_init_valid(self):
        """Test TLV parameter initialization with valid data."""
        tlv = TLVParameter(0x1234, b'test_value')
        assert tlv.tag == 0x1234
        assert tlv.length == 10
        assert tlv.value == b'test_value'

    def test_init_empty_value(self):
        """Test TLV parameter with empty value."""
        tlv = TLVParameter(0x0000, b'')
        assert tlv.tag == 0x0000
        assert tlv.length == 0
        assert tlv.value == b''

    def test_init_max_tag(self):
        """Test TLV parameter with maximum tag value."""
        tlv = TLVParameter(0xFFFF, b'test')
        assert tlv.tag == 0xFFFF
        assert tlv.length == 4
        assert tlv.value == b'test'

    def test_init_invalid_tag_negative(self):
        """Test TLV parameter with invalid negative tag."""
        with pytest.raises(SMPPPDUException, match='Invalid TLV tag: -1'):
            TLVParameter(-1, b'test')

    def test_init_invalid_tag_too_large(self):
        """Test TLV parameter with tag too large."""
        with pytest.raises(SMPPPDUException, match='Invalid TLV tag: 65536'):
            TLVParameter(0x10000, b'test')

    def test_init_value_too_long(self):
        """Test TLV parameter with value too long."""
        long_value = b'x' * (0xFFFF + 1)
        with pytest.raises(SMPPPDUException, match='TLV value too long: 65536 bytes'):
            TLVParameter(0x1234, long_value)

    def test_encode(self):
        """Test TLV parameter encoding."""
        tlv = TLVParameter(0x1234, b'test')
        encoded = tlv.encode()

        # Expected: tag (2 bytes) + length (2 bytes) + value (4 bytes)
        expected = struct.pack('>HH', 0x1234, 4) + b'test'
        assert encoded == expected

    def test_encode_empty_value(self):
        """Test encoding TLV with empty value."""
        tlv = TLVParameter(0x5678, b'')
        encoded = tlv.encode()

        expected = struct.pack('>HH', 0x5678, 0)
        assert encoded == expected

    def test_decode_valid(self):
        """Test TLV parameter decoding."""
        data = struct.pack('>HH', 0x1234, 4) + b'test'
        tlv, offset = TLVParameter.decode(data)

        assert tlv.tag == 0x1234
        assert tlv.length == 4
        assert tlv.value == b'test'
        assert offset == 8

    def test_decode_with_offset(self):
        """Test TLV parameter decoding with offset."""
        prefix = b'prefix'
        data = prefix + struct.pack('>HH', 0xABCD, 3) + b'xyz'
        tlv, offset = TLVParameter.decode(data, len(prefix))

        assert tlv.tag == 0xABCD
        assert tlv.length == 3
        assert tlv.value == b'xyz'
        assert offset == len(prefix) + 7

    def test_decode_empty_value(self):
        """Test decoding TLV with empty value."""
        data = struct.pack('>HH', 0x0000, 0)
        tlv, offset = TLVParameter.decode(data)

        assert tlv.tag == 0x0000
        assert tlv.length == 0
        assert tlv.value == b''
        assert offset == 4

    def test_decode_insufficient_header_data(self):
        """Test decoding with insufficient header data."""
        data = b'123'  # Only 3 bytes, need 4 for header
        with pytest.raises(SMPPPDUException, match='Insufficient data for TLV header'):
            TLVParameter.decode(data)

    def test_decode_insufficient_value_data(self):
        """Test decoding with insufficient value data."""
        data = (
            struct.pack('>HH', 0x1234, 10) + b'short'
        )  # Claims 10 bytes but only has 5
        with pytest.raises(SMPPPDUException, match='Insufficient data for TLV value'):
            TLVParameter.decode(data)

    def test_repr(self):
        """Test TLV parameter string representation."""
        tlv = TLVParameter(0x1234, b'test')
        expected = "TLVParameter(tag=0x1234, length=4, value=b'test')"
        assert repr(tlv) == expected

    def test_equality(self):
        """Test TLV parameter equality."""
        tlv1 = TLVParameter(0x1234, b'test')
        tlv2 = TLVParameter(0x1234, b'test')
        tlv3 = TLVParameter(0x1234, b'different')
        tlv4 = TLVParameter(0x5678, b'test')

        assert tlv1 == tlv2
        assert tlv1 != tlv3
        assert tlv1 != tlv4
        assert tlv1 != 'not a tlv'

    def test_hash(self):
        """Test TLV parameter hashing."""
        tlv1 = TLVParameter(0x1234, b'test')
        tlv2 = TLVParameter(0x1234, b'test')
        tlv3 = TLVParameter(0x1234, b'different')

        assert hash(tlv1) == hash(tlv2)
        assert hash(tlv1) != hash(tlv3)

        # Test that TLV can be used in sets
        tlv_set = {tlv1, tlv2, tlv3}
        assert len(tlv_set) == 2  # tlv1 and tlv2 are equal


class TestPDU:
    """Test PDU base class."""

    def test_generate_sequence_number(self):
        """Test sequence number generation."""
        with patch('time.time', return_value=1234.567):
            seq_num = PDU._generate_sequence_number()
            expected = int(1234.567 * 1000) % 0x7FFFFFFF
            assert seq_num == expected

    def test_generate_sequence_number_bounds(self):
        """Test sequence number is within valid bounds."""
        seq_num = PDU._generate_sequence_number()
        assert 1 <= seq_num <= 0x7FFFFFFF

    def test_post_init_generates_sequence(self):
        """Test that __post_init__ generates sequence number when 0."""

        # Create a concrete PDU subclass for testing
        class TestPDU(PDU):
            def encode_body(self):
                return b''

            def decode_body(self, data, offset=0):
                return offset

        with patch('time.time', return_value=1000.0):
            pdu = TestPDU()
            assert pdu.sequence_number == 1000000 % 0x7FFFFFFF

    def test_post_init_preserves_sequence(self):
        """Test that __post_init__ preserves non-zero sequence number."""

        class TestPDU(PDU):
            def encode_body(self):
                return b''

            def decode_body(self, data, offset=0):
                return offset

        pdu = TestPDU(sequence_number=12345)
        assert pdu.sequence_number == 12345

    def test_default_values(self):
        """Test PDU default values."""

        class TestPDU(PDU):
            def encode_body(self):
                return b''

            def decode_body(self, data, offset=0):
                return offset

        pdu = TestPDU()
        assert pdu.command_id == 0
        assert pdu.command_status == CommandStatus.ESME_ROK
        assert pdu.sequence_number != 0  # Generated automatically
        assert pdu.optional_parameters == []

    def test_custom_values(self):
        """Test PDU with custom values."""

        class TestPDU(PDU):
            def encode_body(self):
                return b''

            def decode_body(self, data, offset=0):
                return offset

        tlv = TLVParameter(0x1234, b'test')
        pdu = TestPDU(
            command_id=0x80000001,
            command_status=CommandStatus.ESME_RINVMSGLEN,
            sequence_number=42,
            optional_parameters=[tlv],
        )

        assert pdu.command_id == 0x80000001
        assert pdu.command_status == CommandStatus.ESME_RINVMSGLEN
        assert pdu.sequence_number == 42
        assert pdu.optional_parameters == [tlv]


class TestBindRequestPDU:
    """Test BindRequestPDU base class."""

    def test_default_values(self):
        """Test BindRequestPDU default values."""

        class TestBindRequest(BindRequestPDU):
            def encode_body(self):
                return b''

            def decode_body(self, data, offset=0):
                return offset

        pdu = TestBindRequest()
        assert pdu.system_id == ''
        assert pdu.password == ''
        assert pdu.system_type == ''
        assert pdu.interface_version == 52
        assert pdu.addr_ton == 0
        assert pdu.addr_npi == 0
        assert pdu.address_range == ''

    def test_custom_values(self):
        """Test BindRequestPDU with custom values."""

        class TestBindRequest(BindRequestPDU):
            def encode_body(self):
                return b''

            def decode_body(self, data, offset=0):
                return offset

        pdu = TestBindRequest(
            system_id='test_system',
            password='secret',
            system_type='TEST',
            interface_version=53,
            addr_ton=1,
            addr_npi=1,
            address_range='12345*',
        )

        assert pdu.system_id == 'test_system'
        assert pdu.password == 'secret'
        assert pdu.system_type == 'TEST'
        assert pdu.interface_version == 53
        assert pdu.addr_ton == 1
        assert pdu.addr_npi == 1
        assert pdu.address_range == '12345*'


class TestMessagePDU:
    """Test MessagePDU base class."""

    def test_default_values(self):
        """Test MessagePDU default values."""

        class TestMessage(MessagePDU):
            def encode_body(self):
                return b''

            def decode_body(self, data, offset=0):
                return offset

        pdu = TestMessage()
        assert pdu.service_type == ''
        assert pdu.source_addr_ton == 0
        assert pdu.source_addr_npi == 0
        assert pdu.source_addr == ''
        assert pdu.dest_addr_ton == 0
        assert pdu.dest_addr_npi == 0
        assert pdu.destination_addr == ''
        assert pdu.esm_class == 0
        assert pdu.protocol_id == 0
        assert pdu.priority_flag == 0
        assert pdu.schedule_delivery_time == ''
        assert pdu.validity_period == ''
        assert pdu.registered_delivery == 0
        assert pdu.replace_if_present_flag == 0
        assert pdu.data_coding == 0
        assert pdu.sm_default_msg_id == 0
        assert pdu.short_message == b''

    def test_custom_values(self):
        """Test MessagePDU with custom values."""

        class TestMessage(MessagePDU):
            def encode_body(self):
                return b''

            def decode_body(self, data, offset=0):
                return offset

        pdu = TestMessage(
            service_type='SMS',
            source_addr_ton=1,
            source_addr_npi=1,
            source_addr='12345',
            dest_addr_ton=1,
            dest_addr_npi=1,
            destination_addr='67890',
            esm_class=0x03,
            protocol_id=0,
            priority_flag=1,
            schedule_delivery_time='',
            validity_period='',
            registered_delivery=1,
            replace_if_present_flag=0,
            data_coding=0,
            sm_default_msg_id=0,
            short_message=b'Hello World',
        )

        assert pdu.service_type == 'SMS'
        assert pdu.source_addr_ton == 1
        assert pdu.source_addr_npi == 1
        assert pdu.source_addr == '12345'
        assert pdu.dest_addr_ton == 1
        assert pdu.dest_addr_npi == 1
        assert pdu.destination_addr == '67890'
        assert pdu.esm_class == 0x03
        assert pdu.protocol_id == 0
        assert pdu.priority_flag == 1
        assert pdu.schedule_delivery_time == ''
        assert pdu.validity_period == ''
        assert pdu.registered_delivery == 1
        assert pdu.replace_if_present_flag == 0
        assert pdu.data_coding == 0
        assert pdu.sm_default_msg_id == 0
        assert pdu.short_message == b'Hello World'
