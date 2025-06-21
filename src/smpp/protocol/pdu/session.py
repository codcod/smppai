"""
SMPP Session PDU Implementations

This module contains session management PDU classes including enquire_link,
generic_nack, and other session-related protocol data units.
"""

import struct
from dataclasses import dataclass
from typing import Optional

from ...exceptions import SMPPPDUException
from ..constants import CommandId
from .base import EmptyBodyPDU, RequestPDU, ResponsePDU


@dataclass
class EnquireLink(EmptyBodyPDU, RequestPDU):
    """ENQUIRE_LINK PDU - Keepalive request to test connection"""

    def __post_init__(self) -> None:
        if self.command_id == 0:
            self.command_id = CommandId.ENQUIRE_LINK
        super().__post_init__()


class EnquireLinkResp(EmptyBodyPDU, ResponsePDU):
    """ENQUIRE_LINK_RESP PDU - Response to enquire_link"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.command_id == 0:
            self.command_id = CommandId.ENQUIRE_LINK_RESP


class GenericNack(EmptyBodyPDU, ResponsePDU):
    """GENERIC_NACK PDU - Generic negative acknowledgment for invalid PDUs"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.command_id == 0:
            self.command_id = CommandId.GENERIC_NACK

    def create_for_invalid_pdu(
        self,
        sequence_number: int,
        error_status: int,
        error_message: Optional[str] = None,
    ) -> 'GenericNack':
        """Create a generic_nack for an invalid PDU

        Args:
            sequence_number: Sequence number from the invalid PDU
            error_status: Error status code
            error_message: Optional error message (not used in encoding)

        Returns:
            GenericNack: This instance for method chaining
        """
        self.sequence_number = sequence_number
        self.command_status = error_status

        if error_message:
            # Add error message as optional parameter
            self.add_optional_parameter(0x001D, error_message.encode('utf-8'))

        return self


@dataclass
class AlertNotification(RequestPDU):
    """ALERT_NOTIFICATION PDU - Notification of message availability"""

    source_addr_ton: int = 0
    source_addr_npi: int = 0
    source_addr: str = ''
    esme_addr_ton: int = 0
    esme_addr_npi: int = 0
    esme_addr: str = ''

    def __post_init__(self) -> None:
        if self.command_id == 0:
            self.command_id = CommandId.ALERT_NOTIFICATION
        super().__post_init__()

    def encode_body(self) -> bytes:
        """Encode alert_notification body

        Returns:
            bytes: Encoded PDU body
        """
        from ..codec import encode_cstring

        return (
            struct.pack('BB', self.source_addr_ton, self.source_addr_npi)
            + encode_cstring(self.source_addr, 21)
            + struct.pack('BB', self.esme_addr_ton, self.esme_addr_npi)
            + encode_cstring(self.esme_addr, 21)
        )

    def decode_body(self, data: bytes, offset: int = 0) -> int:
        """Decode alert_notification body

        Args:
            data: Raw PDU data to decode
            offset: Starting position in data

        Returns:
            int: New offset after decoding

        Raises:
            SMPPPDUException: If data is insufficient
        """
        from ..codec import decode_cstring

        if offset + 2 > len(data):
            raise SMPPPDUException('Insufficient data for source address fields')

        self.source_addr_ton, self.source_addr_npi = struct.unpack(
            'BB', data[offset : offset + 2]
        )
        offset += 2

        self.source_addr, offset = decode_cstring(data, offset, 21)

        if offset + 2 > len(data):
            raise SMPPPDUException('Insufficient data for ESME address fields')

        self.esme_addr_ton, self.esme_addr_npi = struct.unpack(
            'BB', data[offset : offset + 2]
        )
        offset += 2

        self.esme_addr, offset = decode_cstring(data, offset, 21)
        return offset

    def validate(self) -> None:
        """Validate alert_notification fields"""
        super().validate()

        if len(self.source_addr) > 20:
            raise SMPPPDUException('source_addr too long')
        if len(self.esme_addr) > 20:
            raise SMPPPDUException('esme_addr too long')
        if not (0 <= self.source_addr_ton <= 255):
            raise SMPPPDUException('invalid source_addr_ton')
        if not (0 <= self.source_addr_npi <= 255):
            raise SMPPPDUException('invalid source_addr_npi')
        if not (0 <= self.esme_addr_ton <= 255):
            raise SMPPPDUException('invalid esme_addr_ton')
        if not (0 <= self.esme_addr_npi <= 255):
            raise SMPPPDUException('invalid esme_addr_npi')


@dataclass
class DataSm(RequestPDU):
    """DATA_SM PDU - Submit data using optional parameters"""

    service_type: str = ''
    source_addr_ton: int = 0
    source_addr_npi: int = 0
    source_addr: str = ''
    dest_addr_ton: int = 0
    dest_addr_npi: int = 0
    destination_addr: str = ''
    esm_class: int = 0
    registered_delivery: int = 0
    data_coding: int = 0

    def __post_init__(self):
        if self.command_id == 0:
            self.command_id = CommandId.DATA_SM
        super().__post_init__()

    def encode_body(self) -> bytes:
        """Encode data_sm body"""
        from ..codec import encode_cstring

        return (
            encode_cstring(self.service_type, 6)
            + struct.pack('BB', self.source_addr_ton, self.source_addr_npi)
            + encode_cstring(self.source_addr, 21)
            + struct.pack('BB', self.dest_addr_ton, self.dest_addr_npi)
            + encode_cstring(self.destination_addr, 21)
            + struct.pack(
                'BBB', self.esm_class, self.registered_delivery, self.data_coding
            )
        )

    def decode_body(self, data: bytes, offset: int = 0) -> int:
        """Decode data_sm body"""
        from ..codec import decode_cstring

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

        if offset + 3 > len(data):
            raise SMPPPDUException('Insufficient data for data_sm fields')

        self.esm_class, self.registered_delivery, self.data_coding = struct.unpack(
            'BBB', data[offset : offset + 3]
        )
        offset += 3

        return offset

    def validate(self) -> None:
        """Validate data_sm fields"""
        super().validate()

        if len(self.service_type) > 5:
            raise SMPPPDUException('service_type too long')
        if len(self.source_addr) > 20:
            raise SMPPPDUException('source_addr too long')
        if len(self.destination_addr) > 20:
            raise SMPPPDUException('destination_addr too long')
        if not (0 <= self.source_addr_ton <= 255):
            raise SMPPPDUException('invalid source_addr_ton')
        if not (0 <= self.source_addr_npi <= 255):
            raise SMPPPDUException('invalid source_addr_npi')
        if not (0 <= self.dest_addr_ton <= 255):
            raise SMPPPDUException('invalid dest_addr_ton')
        if not (0 <= self.dest_addr_npi <= 255):
            raise SMPPPDUException('invalid dest_addr_npi')
        if not (0 <= self.esm_class <= 255):
            raise SMPPPDUException('invalid esm_class')
        if not (0 <= self.registered_delivery <= 255):
            raise SMPPPDUException('invalid registered_delivery')
        if not (0 <= self.data_coding <= 255):
            raise SMPPPDUException('invalid data_coding')

    def get_message_payload(self) -> bytes:
        """Get message payload from optional parameters"""
        from ..constants import OptionalTag

        return self.get_optional_parameter_value(OptionalTag.MESSAGE_PAYLOAD) or b''

    def set_message_payload(self, payload: bytes) -> None:
        """Set message payload as optional parameter"""
        from ..constants import OptionalTag

        self.add_optional_parameter(OptionalTag.MESSAGE_PAYLOAD, payload)

    def get_message_text(self, encoding: str = 'utf-8') -> str:
        """Get message text from payload"""
        payload = self.get_message_payload()
        try:
            return payload.decode(encoding)
        except UnicodeDecodeError:
            return payload.decode(encoding, errors='replace')

    def set_message_text(self, text: str, encoding: str = 'utf-8') -> None:
        """Set message text as payload"""
        payload = text.encode(encoding)
        self.set_message_payload(payload)


class DataSmResp(ResponsePDU):
    """DATA_SM_RESP PDU - Response to data_sm"""

    def __init__(self, message_id: str = '', **kwargs):
        super().__init__(**kwargs)
        self.message_id = message_id
        if self.command_id == 0:
            self.command_id = CommandId.DATA_SM_RESP

    def encode_body(self) -> bytes:
        """Encode data_sm_resp body"""
        from ..codec import encode_cstring

        return encode_cstring(self.message_id, 65)

    def decode_body(self, data: bytes, offset: int = 0) -> int:
        """Decode data_sm_resp body"""
        from ..codec import decode_cstring

        self.message_id, offset = decode_cstring(data, offset, 65)
        return offset

    def validate(self) -> None:
        """Validate data_sm_resp fields"""
        super().validate()

        if len(self.message_id) >= 65:
            raise SMPPPDUException('message_id too long')


@dataclass
class QuerySm(RequestPDU):
    """QUERY_SM PDU - Query status of a submitted message"""

    message_id: str = ''
    source_addr_ton: int = 0
    source_addr_npi: int = 0
    source_addr: str = ''

    def __post_init__(self):
        if self.command_id == 0:
            self.command_id = CommandId.QUERY_SM
        super().__post_init__()

    def encode_body(self) -> bytes:
        """Encode query_sm body"""
        from ..codec import encode_cstring

        return (
            encode_cstring(self.message_id, 65)
            + struct.pack('BB', self.source_addr_ton, self.source_addr_npi)
            + encode_cstring(self.source_addr, 21)
        )

    def decode_body(self, data: bytes, offset: int = 0) -> int:
        """Decode query_sm body"""
        from ..codec import decode_cstring

        self.message_id, offset = decode_cstring(data, offset, 65)

        if offset + 2 > len(data):
            raise SMPPPDUException('Insufficient data for source address fields')

        self.source_addr_ton, self.source_addr_npi = struct.unpack(
            'BB', data[offset : offset + 2]
        )
        offset += 2

        self.source_addr, offset = decode_cstring(data, offset, 21)
        return offset

    def validate(self) -> None:
        """Validate query_sm fields"""
        super().validate()

        if not self.message_id:
            raise SMPPPDUException('message_id cannot be empty')
        if len(self.message_id) >= 65:
            raise SMPPPDUException('message_id too long')
        if len(self.source_addr) > 20:
            raise SMPPPDUException('source_addr too long')
        if not (0 <= self.source_addr_ton <= 255):
            raise SMPPPDUException('invalid source_addr_ton')
        if not (0 <= self.source_addr_npi <= 255):
            raise SMPPPDUException('invalid source_addr_npi')


class QuerySmResp(ResponsePDU):
    """QUERY_SM_RESP PDU - Response to query_sm"""

    def __init__(
        self,
        message_id: str = '',
        final_date: str = '',
        message_state: int = 0,
        error_code: int = 0,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.message_id = message_id
        self.final_date = final_date
        self.message_state = message_state
        self.error_code = error_code
        if self.command_id == 0:
            self.command_id = CommandId.QUERY_SM_RESP

    def encode_body(self) -> bytes:
        """Encode query_sm_resp body"""
        from ..codec import encode_cstring

        return (
            encode_cstring(self.message_id, 65)
            + encode_cstring(self.final_date, 17)
            + struct.pack('BB', self.message_state, self.error_code)
        )

    def decode_body(self, data: bytes, offset: int = 0) -> int:
        """Decode query_sm_resp body"""
        from ..codec import decode_cstring

        self.message_id, offset = decode_cstring(data, offset, 65)
        self.final_date, offset = decode_cstring(data, offset, 17)

        if offset + 2 > len(data):
            raise SMPPPDUException('Insufficient data for query_sm_resp fields')

        self.message_state, self.error_code = struct.unpack(
            'BB', data[offset : offset + 2]
        )
        offset += 2

        return offset

    def validate(self) -> None:
        """Validate query_sm_resp fields"""
        super().validate()

        if len(self.message_id) >= 65:
            raise SMPPPDUException('message_id too long')
        if len(self.final_date) > 16:
            raise SMPPPDUException('final_date too long')
        if not (0 <= self.message_state <= 255):
            raise SMPPPDUException('invalid message_state')
        if not (0 <= self.error_code <= 255):
            raise SMPPPDUException('invalid error_code')

    def get_message_state_name(self) -> str:
        """Get human-readable message state name

        Returns:
            str: Human-readable message state name
        """
        from ..constants import MessageState

        state_names = {
            MessageState.ENROUTE: 'ENROUTE',
            MessageState.DELIVERED: 'DELIVERED',
            MessageState.EXPIRED: 'EXPIRED',
            MessageState.DELETED: 'DELETED',
            MessageState.UNDELIVERABLE: 'UNDELIVERABLE',
            MessageState.ACCEPTED: 'ACCEPTED',
            MessageState.UNKNOWN: 'UNKNOWN',
            MessageState.REJECTED: 'REJECTED',
        }

        # Convert int to MessageState enum if needed
        try:
            message_state = MessageState(self.message_state)
            return state_names.get(message_state, f'UNKNOWN_{self.message_state}')
        except ValueError:
            return f'UNKNOWN_{self.message_state}'
