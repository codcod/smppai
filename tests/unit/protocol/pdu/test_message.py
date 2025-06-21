"""Unit tests for SMPP message PDUs."""

import pytest

from smpp.exceptions import SMPPPDUException
from smpp.protocol.constants import CommandId, CommandStatus, MAX_SHORT_MESSAGE_LENGTH
from smpp.protocol.pdu.message import (
    StandardMessagePDU,
    SubmitSm,
    SubmitSmResp,
    DeliverSm,
    DeliverSmResp,
)


class TestStandardMessagePDU:
    """Test StandardMessagePDU base class."""

    def test_encode_body_basic(self):
        """Test StandardMessagePDU body encoding with basic data."""

        class TestMessage(StandardMessagePDU):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)

        pdu = TestMessage(
            service_type='SMS',
            source_addr_ton=1,
            source_addr_npi=1,
            source_addr='12345',
            dest_addr_ton=1,
            dest_addr_npi=1,
            destination_addr='67890',
            esm_class=0,
            protocol_id=0,
            priority_flag=0,
            schedule_delivery_time='',
            validity_period='',
            registered_delivery=1,
            replace_if_present_flag=0,
            data_coding=0,
            sm_default_msg_id=0,
            short_message=b'Hello',
        )

        body = pdu.encode_body()

        # Expected encoding: SMS\x00 + \x01\x01 + 12345\x00 + \x01\x01 + 67890\x00 +
        # 6-byte flags + \x00 + \x00 + \x00\x05 + Hello
        expected = (
            b'SMS\x00'  # service_type
            b'\x01\x01'  # source_addr_ton, source_addr_npi
            b'12345\x00'  # source_addr
            b'\x01\x01'  # dest_addr_ton, dest_addr_npi
            b'67890\x00'  # destination_addr
            b'\x00\x00\x00\x01\x00\x00'  # esm_class, protocol_id, priority_flag, registered_delivery, replace_if_present_flag, data_coding
            b'\x00'  # schedule_delivery_time (empty)
            b'\x00'  # validity_period (empty)
            b'\x00\x05'  # sm_default_msg_id, sm_length
            b'Hello'  # short_message
        )
        assert body == expected

    def test_encode_body_message_too_long(self):
        """Test encoding with message too long."""

        class TestMessage(StandardMessagePDU):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)

        long_message = b'x' * (MAX_SHORT_MESSAGE_LENGTH + 1)
        pdu = TestMessage(short_message=long_message)

        with pytest.raises(SMPPPDUException, match='Short message too long'):
            pdu.encode_body()

    def test_decode_body_basic(self):
        """Test StandardMessagePDU body decoding."""

        class TestMessage(StandardMessagePDU):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)

        # Create test data using the actual encoding format
        data = b'SMS\x00\x01\x0112345\x00\x01\x0167890\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x05Hello'

        pdu = TestMessage()
        offset = pdu.decode_body(data)

        assert pdu.service_type == 'SMS'
        assert pdu.source_addr_ton == 1
        assert pdu.source_addr_npi == 1
        assert pdu.source_addr == '12345'
        assert pdu.dest_addr_ton == 1
        assert pdu.dest_addr_npi == 1
        assert pdu.destination_addr == '67890'
        assert pdu.esm_class == 0
        assert pdu.protocol_id == 0
        assert pdu.priority_flag == 0
        assert pdu.registered_delivery == 1
        assert pdu.replace_if_present_flag == 0
        assert pdu.data_coding == 0
        assert pdu.schedule_delivery_time == ''
        assert pdu.validity_period == ''
        assert pdu.sm_default_msg_id == 0
        assert pdu.short_message == b'Hello'
        assert offset == len(data)

    def test_decode_body_insufficient_data_source(self):
        """Test decode with insufficient data for source address fields."""

        class TestMessage(StandardMessagePDU):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)

        short_data = b'SMS\x00\x01'  # Missing source_addr_npi
        pdu = TestMessage()

        with pytest.raises(
            SMPPPDUException, match='Insufficient data for source address fields'
        ):
            pdu.decode_body(short_data)

    def test_decode_body_insufficient_data_dest(self):
        """Test decode with insufficient data for destination address fields."""

        class TestMessage(StandardMessagePDU):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)

        data = b'SMS\x00\x01\x0112345\x00\x01'  # Missing dest_addr_npi
        pdu = TestMessage()

        with pytest.raises(
            SMPPPDUException, match='Insufficient data for destination address fields'
        ):
            pdu.decode_body(data)

    def test_decode_body_insufficient_data_message(self):
        """Test decode with insufficient data for message fields."""

        class TestMessage(StandardMessagePDU):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)

        data = b'SMS\x00\x01\x0112345\x00\x01\x0167890\x00\x00\x00\x00'  # Missing message flags
        pdu = TestMessage()

        with pytest.raises(
            SMPPPDUException, match='Insufficient data for message fields'
        ):
            pdu.decode_body(data)

    def test_is_delivery_receipt_requested(self):
        """Test delivery receipt request checking."""

        class TestMessage(StandardMessagePDU):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)

        pdu = TestMessage(registered_delivery=0x01)
        assert pdu.is_delivery_receipt_requested() is True

        pdu = TestMessage(registered_delivery=0x00)
        assert pdu.is_delivery_receipt_requested() is False

        pdu = TestMessage(registered_delivery=0x02)  # Other bit set
        assert pdu.is_delivery_receipt_requested() is False

    def test_set_delivery_receipt_requested(self):
        """Test setting delivery receipt request."""

        class TestMessage(StandardMessagePDU):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)

        pdu = TestMessage(registered_delivery=0x00)
        pdu.set_delivery_receipt_requested(True)
        assert pdu.registered_delivery & 0x01 == 0x01

        pdu.set_delivery_receipt_requested(False)
        assert pdu.registered_delivery & 0x01 == 0x00

        # Test preserving other bits
        pdu = TestMessage(registered_delivery=0x02)
        pdu.set_delivery_receipt_requested(True)
        assert pdu.registered_delivery == 0x03

        pdu.set_delivery_receipt_requested(False)
        assert pdu.registered_delivery == 0x02

    def test_is_unicode_message(self):
        """Test Unicode message detection."""

        class TestMessage(StandardMessagePDU):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)

        from smpp.protocol.constants import DataCoding

        pdu = TestMessage(data_coding=DataCoding.UCS2)
        assert pdu.is_unicode_message() is True

        pdu = TestMessage(data_coding=DataCoding.DEFAULT)
        assert pdu.is_unicode_message() is False

    def test_get_message_encoding(self):
        """Test message encoding detection."""

        class TestMessage(StandardMessagePDU):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)

        from smpp.protocol.constants import DataCoding

        pdu = TestMessage(data_coding=DataCoding.DEFAULT)
        assert pdu.get_message_encoding() == 'latin-1'

        pdu = TestMessage(data_coding=DataCoding.IA5_ASCII)
        assert pdu.get_message_encoding() == 'ascii'

        pdu = TestMessage(data_coding=DataCoding.LATIN_1)
        assert pdu.get_message_encoding() == 'latin-1'

        pdu = TestMessage(data_coding=DataCoding.UCS2)
        assert pdu.get_message_encoding() == 'utf-16-be'

        pdu = TestMessage(data_coding=99)  # Unknown
        assert pdu.get_message_encoding() == 'utf-8'


class TestSubmitSm:
    """Test SubmitSm PDU."""

    def test_init_default(self):
        """Test SubmitSm initialization with defaults."""
        pdu = SubmitSm()
        assert pdu.command_id == CommandId.SUBMIT_SM
        assert pdu.command_status == CommandStatus.ESME_ROK
        assert pdu.service_type == ''
        assert pdu.short_message == b''

    def test_init_custom(self):
        """Test SubmitSm with custom values."""
        pdu = SubmitSm(
            service_type='SMS',
            source_addr='12345',
            destination_addr='67890',
            short_message=b'Test message',
            sequence_number=42,
        )
        assert pdu.command_id == CommandId.SUBMIT_SM
        assert pdu.service_type == 'SMS'
        assert pdu.source_addr == '12345'
        assert pdu.destination_addr == '67890'
        assert pdu.short_message == b'Test message'
        assert pdu.sequence_number == 42

    def test_custom_command_id_preserved(self):
        """Test that custom command_id is preserved."""
        pdu = SubmitSm(command_id=0x12345678)
        assert pdu.command_id == 0x12345678


class TestSubmitSmResp:
    """Test SubmitSmResp PDU."""

    def test_init_default(self):
        """Test SubmitSmResp initialization."""
        pdu = SubmitSmResp()
        assert pdu.command_id == CommandId.SUBMIT_SM_RESP
        assert pdu.command_status == CommandStatus.ESME_ROK
        assert pdu.message_id == ''

    def test_init_custom(self):
        """Test SubmitSmResp with custom values."""
        pdu = SubmitSmResp(
            message_id='MSG123456',
            command_status=CommandStatus.ESME_ROK,
            sequence_number=42,
        )
        assert pdu.command_id == CommandId.SUBMIT_SM_RESP
        assert pdu.message_id == 'MSG123456'
        assert pdu.command_status == CommandStatus.ESME_ROK
        assert pdu.sequence_number == 42

    def test_encode_body(self):
        """Test SubmitSmResp body encoding."""
        pdu = SubmitSmResp(message_id='MSG123')
        body = pdu.encode_body()
        assert body == b'MSG123\x00'

    def test_encode_body_empty(self):
        """Test SubmitSmResp body encoding with empty message_id."""
        pdu = SubmitSmResp(message_id='')
        body = pdu.encode_body()
        assert body == b'\x00'

    def test_decode_body(self):
        """Test SubmitSmResp body decoding."""
        data = b'MESSAGE_ID_12345\x00'
        pdu = SubmitSmResp()
        offset = pdu.decode_body(data)

        assert pdu.message_id == 'MESSAGE_ID_12345'
        assert offset == len(data)

    def test_decode_body_empty(self):
        """Test SubmitSmResp body decoding with empty message_id."""
        data = b'\x00'
        pdu = SubmitSmResp()
        offset = pdu.decode_body(data)

        assert pdu.message_id == ''
        assert offset == 1


class TestDeliverSm:
    """Test DeliverSm PDU."""

    def test_init_default(self):
        """Test DeliverSm initialization."""
        pdu = DeliverSm()
        assert pdu.command_id == CommandId.DELIVER_SM
        assert pdu.command_status == CommandStatus.ESME_ROK

    def test_init_custom(self):
        """Test DeliverSm with custom values."""
        pdu = DeliverSm(
            service_type='SMS',
            source_addr='12345',
            destination_addr='67890',
            short_message=b'Incoming message',
            sequence_number=42,
        )
        assert pdu.command_id == CommandId.DELIVER_SM
        assert pdu.service_type == 'SMS'
        assert pdu.source_addr == '12345'
        assert pdu.destination_addr == '67890'
        assert pdu.short_message == b'Incoming message'
        assert pdu.sequence_number == 42

    def test_is_delivery_receipt(self):
        """Test delivery receipt detection."""
        pdu = DeliverSm(esm_class=0x04)  # Delivery receipt flag
        assert pdu.is_delivery_receipt() is True

        pdu = DeliverSm(esm_class=0x00)
        assert pdu.is_delivery_receipt() is False

        pdu = DeliverSm(esm_class=0x03)  # Other bits set but not 0x04
        assert pdu.is_delivery_receipt() is False


class TestDeliverSmResp:
    """Test DeliverSmResp PDU."""

    def test_init_default(self):
        """Test DeliverSmResp initialization."""
        pdu = DeliverSmResp()
        assert pdu.command_id == CommandId.DELIVER_SM_RESP
        assert pdu.command_status == CommandStatus.ESME_ROK
        assert pdu.message_id == ''

    def test_init_custom(self):
        """Test DeliverSmResp with custom values."""
        pdu = DeliverSmResp(
            message_id='DELIVERY123',
            command_status=CommandStatus.ESME_ROK,
            sequence_number=42,
        )
        assert pdu.command_id == CommandId.DELIVER_SM_RESP
        assert pdu.message_id == 'DELIVERY123'
        assert pdu.sequence_number == 42

    def test_encode_body(self):
        """Test DeliverSmResp body encoding."""
        pdu = DeliverSmResp(message_id='DEL456')
        body = pdu.encode_body()
        assert body == b'DEL456\x00'

    def test_decode_body(self):
        """Test DeliverSmResp body decoding."""
        data = b'DELIVERY_MSG_789\x00'
        pdu = DeliverSmResp()
        offset = pdu.decode_body(data)

        assert pdu.message_id == 'DELIVERY_MSG_789'
        assert offset == len(data)
