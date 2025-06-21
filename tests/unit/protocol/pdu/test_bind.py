"""Unit tests for SMPP bind PDUs."""

import pytest
import struct

from smpp.exceptions import SMPPPDUException
from smpp.protocol.constants import CommandId, CommandStatus
from smpp.protocol.pdu.bind import (
    BindTransmitter,
    BindTransmitterResp,
    BindReceiver,
    BindReceiverResp,
    BindTransceiver,
    BindTransceiverResp,
    Unbind,
    UnbindResp,
    Outbind,
)


class TestBindTransmitter:
    """Test BindTransmitter PDU."""

    def test_init_default(self):
        """Test BindTransmitter initialization with defaults."""
        pdu = BindTransmitter()
        assert pdu.command_id == CommandId.BIND_TRANSMITTER
        assert pdu.command_status == CommandStatus.ESME_ROK
        assert pdu.system_id == ''
        assert pdu.password == ''
        assert pdu.system_type == ''
        assert pdu.interface_version == 52
        assert pdu.addr_ton == 0
        assert pdu.addr_npi == 0
        assert pdu.address_range == ''

    def test_init_custom(self):
        """Test BindTransmitter with custom values."""
        pdu = BindTransmitter(
            system_id='test_system',
            password='secret123',
            system_type='TEST',
            interface_version=53,
            addr_ton=1,
            addr_npi=1,
            address_range='1234*',
            sequence_number=42,
        )
        assert pdu.command_id == CommandId.BIND_TRANSMITTER
        assert pdu.system_id == 'test_system'
        assert pdu.password == 'secret123'
        assert pdu.system_type == 'TEST'
        assert pdu.interface_version == 53
        assert pdu.addr_ton == 1
        assert pdu.addr_npi == 1
        assert pdu.address_range == '1234*'
        assert pdu.sequence_number == 42

    def test_encode_body(self):
        """Test BindTransmitter body encoding."""
        pdu = BindTransmitter(
            system_id='test',
            password='pass',
            system_type='TYPE',
            interface_version=52,
            addr_ton=1,
            addr_npi=1,
            address_range='12345',
        )
        body = pdu.encode_body()

        # The body is a concatenation of encoded fields without padding
        # Expected: test\x00 + pass\x00 + TYPE\x00 + \x34\x01\x01 + 12345\x00
        expected = b'test\x00pass\x00TYPE\x004\x01\x0112345\x00'
        assert body == expected

    def test_decode_body(self):
        """Test BindTransmitter body decoding."""
        # Create test data with null-terminated strings (no padding)
        data = (
            b'test_sys\x00'
            b'pass123\x00'
            b'SMS\x00'
            + struct.pack('BBB', 53, 2, 2)  # version, ton, npi
            + b'555*\x00'
        )

        pdu = BindTransmitter()
        offset = pdu.decode_body(data)

        assert pdu.system_id == 'test_sys'
        assert pdu.password == 'pass123'
        assert pdu.system_type == 'SMS'
        assert pdu.interface_version == 53
        assert pdu.addr_ton == 2
        assert pdu.addr_npi == 2
        assert pdu.address_range == '555*'
        assert offset == len(data)

    def test_decode_body_insufficient_data(self):
        """Test decode with insufficient data."""
        pdu = BindTransmitter()
        short_data = b'short'

        with pytest.raises(SMPPPDUException, match='String not null-terminated'):
            pdu.decode_body(short_data)


class TestBindTransmitterResp:
    """Test BindTransmitterResp PDU."""

    def test_init_default(self):
        """Test BindTransmitterResp initialization."""
        pdu = BindTransmitterResp()
        assert pdu.command_id == CommandId.BIND_TRANSMITTER_RESP
        assert pdu.system_id == ''

    def test_init_custom(self):
        """Test BindTransmitterResp with custom values."""
        pdu = BindTransmitterResp(
            system_id='smsc_system',
            command_status=CommandStatus.ESME_ROK,
            sequence_number=42,
        )
        assert pdu.command_id == CommandId.BIND_TRANSMITTER_RESP
        assert pdu.system_id == 'smsc_system'
        assert pdu.command_status == CommandStatus.ESME_ROK
        assert pdu.sequence_number == 42

    def test_encode_body(self):
        """Test BindTransmitterResp body encoding."""
        pdu = BindTransmitterResp(system_id='test_smsc')
        body = pdu.encode_body()

        # Should be null-terminated system_id
        expected = b'test_smsc\x00'
        assert body == expected

    def test_decode_body(self):
        """Test BindTransmitterResp body decoding."""
        data = b'smsc_name\x00'
        pdu = BindTransmitterResp()
        offset = pdu.decode_body(data)

        assert pdu.system_id == 'smsc_name'
        assert offset == len(data)


class TestBindReceiver:
    """Test BindReceiver PDU."""

    def test_init(self):
        """Test BindReceiver initialization."""
        pdu = BindReceiver()
        assert pdu.command_id == CommandId.BIND_RECEIVER

    def test_custom_command_id_preserved(self):
        """Test that custom command_id is preserved."""
        pdu = BindReceiver(command_id=0x12345678)
        assert pdu.command_id == 0x12345678


class TestBindReceiverResp:
    """Test BindReceiverResp PDU."""

    def test_init(self):
        """Test BindReceiverResp initialization."""
        pdu = BindReceiverResp()
        assert pdu.command_id == CommandId.BIND_RECEIVER_RESP


class TestBindTransceiver:
    """Test BindTransceiver PDU."""

    def test_init(self):
        """Test BindTransceiver initialization."""
        pdu = BindTransceiver()
        assert pdu.command_id == CommandId.BIND_TRANSCEIVER


class TestBindTransceiverResp:
    """Test BindTransceiverResp PDU."""

    def test_init(self):
        """Test BindTransceiverResp initialization."""
        pdu = BindTransceiverResp()
        assert pdu.command_id == CommandId.BIND_TRANSCEIVER_RESP


class TestUnbind:
    """Test Unbind PDU."""

    def test_init(self):
        """Test Unbind initialization."""
        pdu = Unbind()
        assert pdu.command_id == CommandId.UNBIND

    def test_encode_body(self):
        """Test Unbind body encoding (should be empty)."""
        pdu = Unbind()
        body = pdu.encode_body()
        assert body == b''

    def test_decode_body(self):
        """Test Unbind body decoding (should handle empty body)."""
        pdu = Unbind()
        offset = pdu.decode_body(b'')
        assert offset == 0


class TestUnbindResp:
    """Test UnbindResp PDU."""

    def test_init(self):
        """Test UnbindResp initialization."""
        pdu = UnbindResp()
        assert pdu.command_id == CommandId.UNBIND_RESP

    def test_encode_body(self):
        """Test UnbindResp body encoding (should be empty)."""
        pdu = UnbindResp()
        body = pdu.encode_body()
        assert body == b''


class TestOutbind:
    """Test Outbind PDU."""

    def test_init(self):
        """Test Outbind initialization."""
        pdu = Outbind()
        assert pdu.command_id == CommandId.OUTBIND

    def test_encode_body(self):
        """Test Outbind body encoding."""
        pdu = Outbind(system_id='test_system', password='secret')
        body = pdu.encode_body()

        # Expected: test_system\x00 + secret\x00
        expected = b'test_system\x00secret\x00'
        assert body == expected

    def test_decode_body(self):
        """Test Outbind body decoding."""
        data = b'my_system\x00mypass\x00'

        pdu = Outbind()
        offset = pdu.decode_body(data)

        assert pdu.system_id == 'my_system'
        assert pdu.password == 'mypass'
        assert offset == len(data)

    def test_validate_success(self):
        """Test Outbind validation success."""
        pdu = Outbind(system_id='valid_id', password='pass')
        # Should not raise
        pdu.validate()

    def test_validate_empty_system_id(self):
        """Test Outbind validation with empty system_id."""
        pdu = Outbind(system_id='', password='pass')
        with pytest.raises(SMPPPDUException, match='system_id cannot be empty'):
            pdu.validate()

    def test_validate_system_id_too_long(self):
        """Test Outbind validation with system_id too long."""
        pdu = Outbind(
            system_id='x' * 16,  # 16 chars is too long (max 15)
            password='pass',
        )
        with pytest.raises(SMPPPDUException, match='Failed to calculate PDU length'):
            pdu.validate()

    def test_validate_password_too_long(self):
        """Test Outbind validation with password too long."""
        pdu = Outbind(
            system_id='valid',
            password='x' * 9,  # 9 chars is too long (max 8)
        )
        with pytest.raises(SMPPPDUException, match='Failed to calculate PDU length'):
            pdu.validate()
