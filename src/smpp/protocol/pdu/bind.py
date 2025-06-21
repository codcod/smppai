"""
SMPP Bind PDU Implementations

This module contains all bind-related PDU classes including bind requests and responses
for transmitter, receiver, and transceiver modes.
"""

import struct

from ...exceptions import SMPPPDUException, SMPPValidationException
from ..codec import decode_cstring, encode_cstring
from ..constants import CommandId
from ..validation import validate_bind_parameters
from .base import BindRequestPDU, BindResponsePDU, EmptyBodyPDU


class StandardBindRequestPDU(BindRequestPDU):
    """Base class for standard bind requests (transmitter, receiver, transceiver)"""

    def encode_body(self) -> bytes:
        """Encode standard bind request body with all fields"""
        # Validate bind parameters before encoding - convert validation errors for compatibility
        try:
            validate_bind_parameters(
                self.system_id,
                self.password,
                self.system_type,
                self.interface_version,
                self.addr_ton,
                self.addr_npi,
                self.address_range,
            )
        except SMPPValidationException as e:
            raise SMPPPDUException(f'Invalid bind parameters: {e}')

        return (
            encode_cstring(self.system_id, 16)
            + encode_cstring(self.password, 9)
            + encode_cstring(self.system_type, 13)
            + struct.pack('BBB', self.interface_version, self.addr_ton, self.addr_npi)
            + encode_cstring(self.address_range, 41)
        )

    def decode_body(self, data: bytes, offset: int = 0) -> int:
        """Decode standard bind request body with all fields"""
        self.system_id, offset = decode_cstring(data, offset, 16)
        self.password, offset = decode_cstring(data, offset, 9)
        self.system_type, offset = decode_cstring(data, offset, 13)

        if offset + 3 > len(data):
            raise SMPPPDUException('Insufficient data for bind fields')

        self.interface_version, self.addr_ton, self.addr_npi = struct.unpack(
            'BBB', data[offset : offset + 3]
        )
        offset += 3

        self.address_range, offset = decode_cstring(data, offset, 41)
        return offset


class StandardBindResponsePDU(BindResponsePDU):
    """Base class for standard bind responses with system_id only"""

    def encode_body(self) -> bytes:
        """Encode standard bind response body"""
        return encode_cstring(self.system_id, 16)

    def decode_body(self, data: bytes, offset: int = 0) -> int:
        """Decode standard bind response body"""
        self.system_id, offset = decode_cstring(data, offset, 16)
        return offset


class BindTransmitter(StandardBindRequestPDU):
    """BIND_TRANSMITTER PDU - Request to bind as transmitter"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.command_id == 0:
            self.command_id = CommandId.BIND_TRANSMITTER


class BindTransmitterResp(StandardBindResponsePDU):
    """BIND_TRANSMITTER_RESP PDU - Response to bind_transmitter"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.command_id == 0:
            self.command_id = CommandId.BIND_TRANSMITTER_RESP


class BindReceiver(StandardBindRequestPDU):
    """BIND_RECEIVER PDU - Request to bind as receiver"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.command_id == 0:
            self.command_id = CommandId.BIND_RECEIVER


class BindReceiverResp(StandardBindResponsePDU):
    """BIND_RECEIVER_RESP PDU - Response to bind_receiver"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.command_id == 0:
            self.command_id = CommandId.BIND_RECEIVER_RESP


class BindTransceiver(StandardBindRequestPDU):
    """BIND_TRANSCEIVER PDU - Request to bind as transceiver"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.command_id == 0:
            self.command_id = CommandId.BIND_TRANSCEIVER


class BindTransceiverResp(StandardBindResponsePDU):
    """BIND_TRANSCEIVER_RESP PDU - Response to bind_transceiver"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.command_id == 0:
            self.command_id = CommandId.BIND_TRANSCEIVER_RESP


class Unbind(EmptyBodyPDU):
    """UNBIND PDU - Request to unbind from SMSC"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.command_id == 0:
            self.command_id = CommandId.UNBIND


class UnbindResp(EmptyBodyPDU):
    """UNBIND_RESP PDU - Response to unbind"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.command_id == 0:
            self.command_id = CommandId.UNBIND_RESP


class Outbind(BindRequestPDU):
    """OUTBIND PDU - SMSC initiated bind request"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.command_id == 0:
            self.command_id = CommandId.OUTBIND

    def encode_body(self) -> bytes:
        """Encode outbind body with system_id and password only"""
        return encode_cstring(self.system_id, 16) + encode_cstring(self.password, 9)

    def decode_body(self, data: bytes, offset: int = 0) -> int:
        """Decode outbind body with system_id and password only"""
        self.system_id, offset = decode_cstring(data, offset, 16)
        self.password, offset = decode_cstring(data, offset, 9)
        return offset

    def validate(self) -> None:
        """Validate outbind fields

        Raises:
            SMPPPDUException: If validation fails
        """
        super().validate()

        if not self.system_id:
            raise SMPPPDUException('system_id cannot be empty for outbind')
        if len(self.system_id) >= 16:
            raise SMPPPDUException(f'system_id too long: {len(self.system_id)} >= 16')
        if len(self.password) >= 9:
            raise SMPPPDUException(f'password too long: {len(self.password)} >= 9')
