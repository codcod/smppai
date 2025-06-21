"""
SMPP Message PDU Implementations

This module contains all message-related PDU classes including submit_sm, deliver_sm,
and their corresponding response PDUs for SMS message handling.
"""

import struct
from dataclasses import dataclass
from typing import Optional

from ...exceptions import SMPPPDUException, SMPPValidationException
from ..codec import decode_cstring, encode_cstring
from ..constants import MAX_SHORT_MESSAGE_LENGTH, CommandId
from ..validation import validate_submit_sm_parameters
from .base import MessagePDU, RequestPDU, ResponsePDU


class StandardMessagePDU(MessagePDU):
    """Base class for standard message PDUs (SubmitSm, DeliverSm) with identical structure"""

    def encode_body(self) -> bytes:
        """Encode standard message PDU body

        Returns:
            bytes: Encoded PDU body

        Raises:
            SMPPPDUException: If short message is too long
        """
        if len(self.short_message) > MAX_SHORT_MESSAGE_LENGTH:
            raise SMPPPDUException(
                f'Short message too long: {len(self.short_message)} > {MAX_SHORT_MESSAGE_LENGTH}'
            )

        # Validate submit_sm parameters before encoding - convert validation errors for compatibility
        try:
            validate_submit_sm_parameters(
                self.source_addr,
                self.destination_addr,
                self.short_message,
                self.source_addr_ton,
                self.source_addr_npi,
                self.dest_addr_ton,
                self.dest_addr_npi,
                self.data_coding,
                self.esm_class,
                self.priority_flag,
                self.registered_delivery,
                self.service_type,
            )
        except SMPPValidationException as e:
            raise SMPPPDUException(f'Invalid message parameters: {e}')

        return (
            encode_cstring(self.service_type, 6)
            + struct.pack('BB', self.source_addr_ton, self.source_addr_npi)
            + encode_cstring(self.source_addr, 21)
            + struct.pack('BB', self.dest_addr_ton, self.dest_addr_npi)
            + encode_cstring(self.destination_addr, 21)
            + struct.pack(
                'BBBBBB',
                self.esm_class,
                self.protocol_id,
                self.priority_flag,
                self.registered_delivery,
                self.replace_if_present_flag,
                self.data_coding,
            )
            + encode_cstring(self.schedule_delivery_time, 17)
            + encode_cstring(self.validity_period, 17)
            + struct.pack('BB', self.sm_default_msg_id, len(self.short_message))
            + self.short_message
        )

    def decode_body(self, data: bytes, offset: int = 0) -> int:
        """Decode standard message PDU body

        Args:
            data: Raw PDU data to decode
            offset: Starting position in data

        Returns:
            int: New offset after decoding

        Raises:
            SMPPPDUException: If data is insufficient or invalid
        """
        self.service_type, offset = decode_cstring(data, offset, 6)

        if offset + 2 > len(data):
            raise SMPPPDUException('Insufficient data for source address fields')

        self.source_addr_ton, self.source_addr_npi = struct.unpack(
            'BB', data[offset : offset + 2]
        )
        offset += 2

        self.source_addr, offset = decode_cstring(data, offset, 21)

        if offset + 2 > len(data):
            raise SMPPPDUException('Insufficient data for destination address fields')

        self.dest_addr_ton, self.dest_addr_npi = struct.unpack(
            'BB', data[offset : offset + 2]
        )
        offset += 2

        self.destination_addr, offset = decode_cstring(data, offset, 21)

        if offset + 6 > len(data):
            raise SMPPPDUException('Insufficient data for message fields')

        (
            self.esm_class,
            self.protocol_id,
            self.priority_flag,
            self.registered_delivery,
            self.replace_if_present_flag,
            self.data_coding,
        ) = struct.unpack('BBBBBB', data[offset : offset + 6])
        offset += 6

        self.schedule_delivery_time, offset = decode_cstring(data, offset, 17)
        self.validity_period, offset = decode_cstring(data, offset, 17)

        if offset + 2 > len(data):
            raise SMPPPDUException('Insufficient data for message fields')

        self.sm_default_msg_id, sm_length = struct.unpack(
            'BB', data[offset : offset + 2]
        )
        offset += 2

        if offset + sm_length > len(data):
            raise SMPPPDUException('Insufficient data for short message')

        self.short_message = data[offset : offset + sm_length]
        offset += sm_length

        return offset

    def get_message_text(self, encoding: Optional[str] = None) -> str:
        """Get message text as string using specified or auto-detected encoding

        Args:
            encoding: Text encoding to use (auto-detected if not provided)

        Returns:
            str: Decoded message text
        """
        if encoding is None:
            encoding = self.get_message_encoding()

        try:
            return self.short_message.decode(encoding)
        except UnicodeDecodeError:
            return self.short_message.decode(encoding, errors='replace')

    def set_message_text(self, text: str, encoding: Optional[str] = None) -> None:
        """Set message text from string using specified or auto-detected encoding

        Args:
            text: Message text to set
            encoding: Text encoding to use (auto-detected if not provided)
        """
        if encoding is None:
            encoding = self.get_message_encoding()
        self.short_message = text.encode(encoding)

    def is_delivery_receipt_requested(self) -> bool:
        """Check if delivery receipt is requested

        Returns:
            bool: True if delivery receipt is requested
        """
        return bool(self.registered_delivery & 0x01)

    def set_delivery_receipt_requested(self, requested: bool = True) -> None:
        """Set delivery receipt request flag

        Args:
            requested: Whether to request delivery receipt (default: True)
        """
        if requested:
            self.registered_delivery |= 0x01
        else:
            self.registered_delivery &= ~0x01

    def is_unicode_message(self) -> bool:
        """Check if message uses Unicode encoding

        Returns:
            bool: True if message uses Unicode (UCS2) encoding
        """
        from ..constants import DataCoding

        return self.data_coding == DataCoding.UCS2

    def get_message_encoding(self) -> str:
        """Get appropriate encoding for the message based on data_coding

        Returns:
            str: Encoding string for the message
        """
        from ..constants import DataCoding

        if self.data_coding == DataCoding.DEFAULT:
            return 'latin-1'  # GSM 7-bit approximation
        elif self.data_coding == DataCoding.IA5_ASCII:
            return 'ascii'
        elif self.data_coding == DataCoding.LATIN_1:
            return 'latin-1'
        elif self.data_coding == DataCoding.UCS2:
            return 'utf-16-be'
        else:
            return 'utf-8'  # Default fallback


@dataclass
class SubmitSm(StandardMessagePDU, RequestPDU):
    """SUBMIT_SM PDU - Request to submit a short message"""

    service_type: str = ''
    source_addr_ton: int = 0
    source_addr_npi: int = 0
    source_addr: str = ''
    dest_addr_ton: int = 0
    dest_addr_npi: int = 0
    destination_addr: str = ''
    esm_class: int = 0
    protocol_id: int = 0
    priority_flag: int = 0
    schedule_delivery_time: str = ''
    validity_period: str = ''
    registered_delivery: int = 0
    replace_if_present_flag: int = 0
    data_coding: int = 0
    sm_default_msg_id: int = 0
    short_message: bytes = b''

    def __post_init__(self) -> None:
        if self.command_id == 0:
            self.command_id = CommandId.SUBMIT_SM
        super().__post_init__()


@dataclass
class SubmitSmResp(ResponsePDU):
    """SUBMIT_SM_RESP PDU - Response to submit_sm"""

    message_id: str = ''

    def __post_init__(self) -> None:
        if self.command_id == 0:
            self.command_id = CommandId.SUBMIT_SM_RESP
        super().__post_init__()

    def encode_body(self) -> bytes:
        """Encode submit_sm_resp body

        Returns:
            bytes: Encoded PDU body
        """
        return encode_cstring(self.message_id, 65)

    def decode_body(self, data: bytes, offset: int = 0) -> int:
        """Decode submit_sm_resp body

        Args:
            data: Raw PDU data to decode
            offset: Starting position in data

        Returns:
            int: New offset after decoding
        """
        self.message_id, offset = decode_cstring(data, offset, 65)
        return offset

    def validate(self) -> None:
        """Validate submit_sm_resp fields

        Raises:
            SMPPPDUException: If validation fails
        """
        super().validate()

        if len(self.message_id) >= 65:
            raise SMPPPDUException(f'message_id too long: {len(self.message_id)} >= 65')


@dataclass
class DeliverSm(StandardMessagePDU, RequestPDU):
    """DELIVER_SM PDU - Deliver a short message or delivery receipt"""

    service_type: str = ''
    source_addr_ton: int = 0
    source_addr_npi: int = 0
    source_addr: str = ''
    dest_addr_ton: int = 0
    dest_addr_npi: int = 0
    destination_addr: str = ''
    esm_class: int = 0
    protocol_id: int = 0
    priority_flag: int = 0
    schedule_delivery_time: str = ''
    validity_period: str = ''
    registered_delivery: int = 0
    replace_if_present_flag: int = 0
    data_coding: int = 0
    sm_default_msg_id: int = 0
    short_message: bytes = b''

    def __post_init__(self) -> None:
        if self.command_id == 0:
            self.command_id = CommandId.DELIVER_SM
        super().__post_init__()

    def is_delivery_receipt(self) -> bool:
        """Check if this is a delivery receipt

        Returns:
            bool: True if this is a delivery receipt
        """
        return bool(self.esm_class & 0x04)

    def is_mobile_originated(self) -> bool:
        """Check if this is a mobile originated message

        Returns:
            bool: True if this is a mobile originated message
        """
        return not self.is_delivery_receipt()

    def parse_delivery_receipt(self) -> dict:
        """Parse delivery receipt message into structured data

        Returns:
            dict: Parsed delivery receipt data

        Raises:
            SMPPPDUException: If PDU is not a delivery receipt
        """
        if not self.is_delivery_receipt():
            raise SMPPPDUException('PDU is not a delivery receipt')

        receipt_text = self.get_message_text()
        receipt_data = {}

        # Parse standard delivery receipt format
        # id:XXXXXXXXXX sub:SSS dlvrd:DDD submit date:YYMMDDhhmm done date:YYMMDDhhmm stat:DDDDDDD err:EEE text:...
        import re

        patterns = {
            'id': r'id:(\S+)',
            'sub': r'sub:(\d+)',
            'dlvrd': r'dlvrd:(\d+)',
            'submit_date': r'submit date:(\d+)',
            'done_date': r'done date:(\d+)',
            'stat': r'stat:(\w+)',
            'err': r'err:(\d+)',
            'text': r'text:(.*)$',
        }

        for key, pattern in patterns.items():
            match = re.search(pattern, receipt_text, re.IGNORECASE)
            if match:
                receipt_data[key] = match.group(1).strip()

        return receipt_data

    def create_delivery_receipt(
        self,
        original_message_id: str,
        message_state: str,
        submit_date: str = '',
        done_date: str = '',
        error_code: str = '000',
    ) -> None:
        """Create a delivery receipt message

        Args:
            original_message_id: ID of the original message
            message_state: Current state of the message
            submit_date: When message was submitted (optional)
            done_date: When message processing was completed (optional)
            error_code: Error code if any (default: '000')
        """
        self.esm_class |= 0x04  # Set delivery receipt flag

        # Format delivery receipt text
        receipt_text = (
            f'id:{original_message_id} '
            f'sub:001 dlvrd:001 '
            f'submit date:{submit_date} '
            f'done date:{done_date} '
            f'stat:{message_state} '
            f'err:{error_code} '
            f'text:'
        )

        self.short_message = receipt_text.encode('ascii')


@dataclass
class DeliverSmResp(ResponsePDU):
    """DELIVER_SM_RESP PDU - Response to deliver_sm"""

    message_id: str = ''

    def __post_init__(self) -> None:
        if self.command_id == 0:
            self.command_id = CommandId.DELIVER_SM_RESP
        super().__post_init__()

    def encode_body(self) -> bytes:
        """Encode deliver_sm_resp body

        Returns:
            bytes: Encoded PDU body
        """
        return encode_cstring(self.message_id, 65)

    def decode_body(self, data: bytes, offset: int = 0) -> int:
        """Decode deliver_sm_resp body

        Args:
            data: Raw PDU data to decode
            offset: Starting position in data

        Returns:
            int: New offset after decoding
        """
        self.message_id, offset = decode_cstring(data, offset, 65)
        return offset

    def validate(self) -> None:
        """Validate deliver_sm_resp fields

        Raises:
            SMPPPDUException: If validation fails
        """
        super().validate()

        if len(self.message_id) >= 65:
            raise SMPPPDUException(f'message_id too long: {len(self.message_id)} >= 65')
