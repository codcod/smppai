"""Unit tests for SMPP session PDUs."""

import pytest

from smpp.exceptions import SMPPPDUException
from smpp.protocol.constants import CommandId, CommandStatus
from smpp.protocol.pdu.session import (
    EnquireLink,
    EnquireLinkResp,
    GenericNack,
    AlertNotification,
    DataSm,
    DataSmResp,
    QuerySm,
    QuerySmResp,
)


class TestEnquireLink:
    """Test EnquireLink PDU."""

    def test_init_default(self):
        """Test EnquireLink initialization."""
        pdu = EnquireLink()
        assert pdu.command_id == CommandId.ENQUIRE_LINK
        assert pdu.command_status == CommandStatus.ESME_ROK

    def test_custom_command_id_preserved(self):
        """Test that custom command_id is preserved."""
        pdu = EnquireLink(command_id=0x12345678)
        assert pdu.command_id == 0x12345678

    def test_encode_body(self):
        """Test EnquireLink body encoding (should be empty)."""
        pdu = EnquireLink()
        body = pdu.encode_body()
        assert body == b''

    def test_decode_body(self):
        """Test EnquireLink body decoding (should handle empty body)."""
        pdu = EnquireLink()
        offset = pdu.decode_body(b'')
        assert offset == 0

    def test_sequence_number_generation(self):
        """Test that sequence number is auto-generated."""
        pdu = EnquireLink()
        assert pdu.sequence_number != 0

    def test_custom_sequence_number(self):
        """Test custom sequence number."""
        pdu = EnquireLink(sequence_number=42)
        assert pdu.sequence_number == 42


class TestEnquireLinkResp:
    """Test EnquireLinkResp PDU."""

    def test_init_default(self):
        """Test EnquireLinkResp initialization."""
        pdu = EnquireLinkResp()
        assert pdu.command_id == CommandId.ENQUIRE_LINK_RESP
        assert pdu.command_status == CommandStatus.ESME_ROK

    def test_init_custom(self):
        """Test EnquireLinkResp with custom values."""
        pdu = EnquireLinkResp(command_status=CommandStatus.ESME_ROK, sequence_number=42)
        assert pdu.command_id == CommandId.ENQUIRE_LINK_RESP
        assert pdu.command_status == CommandStatus.ESME_ROK
        assert pdu.sequence_number == 42

    def test_encode_body(self):
        """Test EnquireLinkResp body encoding (should be empty)."""
        pdu = EnquireLinkResp()
        body = pdu.encode_body()
        assert body == b''

    def test_decode_body(self):
        """Test EnquireLinkResp body decoding."""
        pdu = EnquireLinkResp()
        offset = pdu.decode_body(b'')
        assert offset == 0


class TestGenericNack:
    """Test GenericNack PDU."""

    def test_init_default(self):
        """Test GenericNack initialization."""
        pdu = GenericNack()
        assert pdu.command_id == CommandId.GENERIC_NACK
        assert pdu.command_status == CommandStatus.ESME_ROK

    def test_init_custom(self):
        """Test GenericNack with custom values."""
        pdu = GenericNack(
            command_status=CommandStatus.ESME_RINVCMDID, sequence_number=42
        )
        assert pdu.command_id == CommandId.GENERIC_NACK
        assert pdu.command_status == CommandStatus.ESME_RINVCMDID
        assert pdu.sequence_number == 42

    def test_encode_body(self):
        """Test GenericNack body encoding (should be empty)."""
        pdu = GenericNack()
        body = pdu.encode_body()
        assert body == b''

    def test_create_for_invalid_pdu_basic(self):
        """Test creating GenericNack for invalid PDU."""
        pdu = GenericNack()
        result = pdu.create_for_invalid_pdu(123, CommandStatus.ESME_RINVCMDID)

        assert result is pdu  # Should return self for chaining
        assert pdu.sequence_number == 123
        assert pdu.command_status == CommandStatus.ESME_RINVCMDID

    def test_create_for_invalid_pdu_with_message(self):
        """Test creating GenericNack with error message."""
        pdu = GenericNack()
        error_msg = 'Invalid command ID'
        result = pdu.create_for_invalid_pdu(
            456, CommandStatus.ESME_RINVCMDID, error_msg
        )

        assert result is pdu
        assert pdu.sequence_number == 456
        assert pdu.command_status == CommandStatus.ESME_RINVCMDID

        # Check that error message was added as optional parameter
        assert len(pdu.optional_parameters) == 1
        assert pdu.optional_parameters[0].tag == 0x001D
        assert pdu.optional_parameters[0].value == error_msg.encode('utf-8')


class TestAlertNotification:
    """Test AlertNotification PDU."""

    def test_init_default(self):
        """Test AlertNotification initialization."""
        pdu = AlertNotification()
        assert pdu.command_id == CommandId.ALERT_NOTIFICATION
        assert pdu.source_addr_ton == 0
        assert pdu.source_addr_npi == 0
        assert pdu.source_addr == ''
        assert pdu.esme_addr_ton == 0
        assert pdu.esme_addr_npi == 0
        assert pdu.esme_addr == ''

    def test_init_custom(self):
        """Test AlertNotification with custom values."""
        pdu = AlertNotification(
            source_addr_ton=1,
            source_addr_npi=1,
            source_addr='12345',
            esme_addr_ton=2,
            esme_addr_npi=2,
            esme_addr='67890',
            sequence_number=42,
        )
        assert pdu.command_id == CommandId.ALERT_NOTIFICATION
        assert pdu.source_addr_ton == 1
        assert pdu.source_addr_npi == 1
        assert pdu.source_addr == '12345'
        assert pdu.esme_addr_ton == 2
        assert pdu.esme_addr_npi == 2
        assert pdu.esme_addr == '67890'
        assert pdu.sequence_number == 42

    def test_encode_body(self):
        """Test AlertNotification body encoding."""
        pdu = AlertNotification(
            source_addr_ton=1,
            source_addr_npi=2,
            source_addr='source',
            esme_addr_ton=3,
            esme_addr_npi=4,
            esme_addr='esme',
        )
        body = pdu.encode_body()

        # Expected: \x01\x02 + source\x00 + \x03\x04 + esme\x00
        expected = b'\x01\x02source\x00\x03\x04esme\x00'
        assert body == expected

    def test_decode_body(self):
        """Test AlertNotification body decoding."""
        data = b'\x01\x02src\x00\x03\x04dest\x00'

        pdu = AlertNotification()
        offset = pdu.decode_body(data)

        assert pdu.source_addr_ton == 1
        assert pdu.source_addr_npi == 2
        assert pdu.source_addr == 'src'
        assert pdu.esme_addr_ton == 3
        assert pdu.esme_addr_npi == 4
        assert pdu.esme_addr == 'dest'
        assert offset == len(data)

    def test_decode_body_insufficient_data(self):
        """Test decode with insufficient data."""
        pdu = AlertNotification()
        short_data = b'short'

        with pytest.raises(SMPPPDUException, match='String not null-terminated'):
            pdu.decode_body(short_data)


class TestDataSm:
    """Test DataSm PDU."""

    def test_init_default(self):
        """Test DataSm initialization."""
        pdu = DataSm()
        assert pdu.command_id == CommandId.DATA_SM
        assert pdu.service_type == ''
        assert pdu.source_addr_ton == 0
        assert pdu.source_addr_npi == 0
        assert pdu.source_addr == ''
        assert pdu.dest_addr_ton == 0
        assert pdu.dest_addr_npi == 0
        assert pdu.destination_addr == ''
        assert pdu.esm_class == 0
        assert pdu.registered_delivery == 0
        assert pdu.data_coding == 0

    def test_init_custom(self):
        """Test DataSm with custom values."""
        pdu = DataSm(
            service_type='SMS',
            source_addr_ton=1,
            source_addr_npi=1,
            source_addr='12345',
            dest_addr_ton=2,
            dest_addr_npi=2,
            destination_addr='67890',
            esm_class=0x03,
            registered_delivery=1,
            data_coding=0,
            sequence_number=42,
        )
        assert pdu.command_id == CommandId.DATA_SM
        assert pdu.service_type == 'SMS'
        assert pdu.source_addr_ton == 1
        assert pdu.source_addr_npi == 1
        assert pdu.source_addr == '12345'
        assert pdu.dest_addr_ton == 2
        assert pdu.dest_addr_npi == 2
        assert pdu.destination_addr == '67890'
        assert pdu.esm_class == 0x03
        assert pdu.registered_delivery == 1
        assert pdu.data_coding == 0
        assert pdu.sequence_number == 42


class TestDataSmResp:
    """Test DataSmResp PDU."""

    def test_init_default(self):
        """Test DataSmResp initialization."""
        pdu = DataSmResp()
        assert pdu.command_id == CommandId.DATA_SM_RESP
        assert pdu.message_id == ''

    def test_init_custom(self):
        """Test DataSmResp with custom values."""
        pdu = DataSmResp(
            message_id='DATA123',
            command_status=CommandStatus.ESME_ROK,
            sequence_number=42,
        )
        assert pdu.command_id == CommandId.DATA_SM_RESP
        assert pdu.message_id == 'DATA123'
        assert pdu.command_status == CommandStatus.ESME_ROK
        assert pdu.sequence_number == 42

    def test_encode_body(self):
        """Test DataSmResp body encoding."""
        pdu = DataSmResp(message_id='MSG456')
        body = pdu.encode_body()
        assert body == b'MSG456\x00'

    def test_decode_body(self):
        """Test DataSmResp body decoding."""
        data = b'DATA_MESSAGE_789\x00'
        pdu = DataSmResp()
        offset = pdu.decode_body(data)

        assert pdu.message_id == 'DATA_MESSAGE_789'
        assert offset == len(data)


class TestQuerySm:
    """Test QuerySm PDU."""

    def test_init_default(self):
        """Test QuerySm initialization."""
        pdu = QuerySm()
        assert pdu.command_id == CommandId.QUERY_SM
        assert pdu.message_id == ''
        assert pdu.source_addr_ton == 0
        assert pdu.source_addr_npi == 0
        assert pdu.source_addr == ''

    def test_init_custom(self):
        """Test QuerySm with custom values."""
        pdu = QuerySm(
            message_id='QUERY123',
            source_addr_ton=1,
            source_addr_npi=1,
            source_addr='12345',
            sequence_number=42,
        )
        assert pdu.command_id == CommandId.QUERY_SM
        assert pdu.message_id == 'QUERY123'
        assert pdu.source_addr_ton == 1
        assert pdu.source_addr_npi == 1
        assert pdu.source_addr == '12345'
        assert pdu.sequence_number == 42

    def test_encode_body(self):
        """Test QuerySm body encoding."""
        pdu = QuerySm(
            message_id='MSG123',
            source_addr_ton=1,
            source_addr_npi=2,
            source_addr='source',
        )
        body = pdu.encode_body()

        # Verify structure
        offset = 0

        # message_id (null-terminated)
        assert body[offset : offset + 7] == b'MSG123\x00'
        offset += len('MSG123\x00')

        # source_addr_ton, source_addr_npi
        assert body[offset : offset + 2] == bytes([1, 2])
        offset += 2

        # source_addr (21 bytes max, null-terminated)
        assert body[offset : offset + 7] == b'source\x00'

    def test_decode_body(self):
        """Test QuerySm body decoding."""
        data = b'MESSAGE_ID\x00\x01\x02src\x00'

        pdu = QuerySm()
        offset = pdu.decode_body(data)

        assert pdu.message_id == 'MESSAGE_ID'
        assert pdu.source_addr_ton == 1
        assert pdu.source_addr_npi == 2
        assert pdu.source_addr == 'src'
        assert offset == len(data)


class TestQuerySmResp:
    """Test QuerySmResp PDU."""

    def test_init_default(self):
        """Test QuerySmResp initialization."""
        pdu = QuerySmResp()
        assert pdu.command_id == CommandId.QUERY_SM_RESP
        assert pdu.message_id == ''
        assert pdu.final_date == ''
        assert pdu.message_state == 0
        assert pdu.error_code == 0

    def test_init_custom(self):
        """Test QuerySmResp with custom values."""
        pdu = QuerySmResp(
            message_id='QUERY_RESP123',
            final_date='210101120000000+',
            message_state=2,
            error_code=0,
            sequence_number=42,
        )
        assert pdu.command_id == CommandId.QUERY_SM_RESP
        assert pdu.message_id == 'QUERY_RESP123'
        assert pdu.final_date == '210101120000000+'
        assert pdu.message_state == 2
        assert pdu.error_code == 0
        assert pdu.sequence_number == 42

    def test_encode_body(self):
        """Test QuerySmResp body encoding."""
        pdu = QuerySmResp(
            message_id='MSG789',
            final_date='210101120000000+',
            message_state=2,
            error_code=0,
        )
        body = pdu.encode_body()

        # Verify structure
        offset = 0

        # message_id (null-terminated)
        assert body[offset : offset + 7] == b'MSG789\x00'
        offset += len('MSG789\x00')

        # final_date (17 bytes max, null-terminated)
        assert body[offset : offset + 17] == b'210101120000000+\x00'
        offset += 17

        # message_state, error_code
        assert body[offset : offset + 2] == bytes([2, 0])

    def test_decode_body(self):
        """Test QuerySmResp body decoding."""
        data = (
            b'MESSAGE_RESP\x00'  # message_id
            + b'210101120000000+\x00'  # final_date (17 bytes)
            + bytes([3, 5])  # message_state, error_code
        )

        pdu = QuerySmResp()
        offset = pdu.decode_body(data)

        assert pdu.message_id == 'MESSAGE_RESP'
        assert pdu.final_date == '210101120000000+'
        assert pdu.message_state == 3
        assert pdu.error_code == 5
        assert offset == len(data)

    def test_decode_body_insufficient_data(self):
        """Test decode with insufficient data."""
        pdu = QuerySmResp()
        short_data = b'MSG\x00'  # Only message_id

        with pytest.raises(SMPPPDUException, match='Insufficient data'):
            pdu.decode_body(short_data)
