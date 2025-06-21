"""
SMPP PDU Module

This module provides complete PDU (Protocol Data Unit) implementations for SMPP v3.4,
including all request and response PDUs, TLV parameter handling, and factory functions.

The module is organized into:
- base: Base PDU classes and utilities
- bind: Bind-related PDUs (transmitter, receiver, transceiver)
- message: Message-related PDUs (submit_sm, deliver_sm)
- session: Session management PDUs (enquire_link, generic_nack, etc.)
- factory: PDU creation and management functions
"""

from .base import (
    PDU,
    BindRequestPDU,
    BindResponsePDU,
    EmptyBodyPDU,
    MessagePDU,
    RequestPDU,
    ResponsePDU,
    TLVParameter,
)
from .bind import (
    BindReceiver,
    BindReceiverResp,
    BindTransceiver,
    BindTransceiverResp,
    BindTransmitter,
    BindTransmitterResp,
    Outbind,
    Unbind,
    UnbindResp,
)
from .factory import (
    PDU_CLASSES,
    create_bind_pdu,
    create_enquire_link_pdu,
    create_error_response,
    create_generic_nack_pdu,
    create_pdu,
    create_request_pdu,
    create_response_pdu,
    create_submit_sm_pdu,
    decode_pdu,
    get_pdu_class,
    get_pdu_name,
    is_command_supported,
)
from .message import DeliverSm, DeliverSmResp, SubmitSm, SubmitSmResp
from .session import (
    AlertNotification,
    DataSm,
    DataSmResp,
    EnquireLink,
    EnquireLinkResp,
    GenericNack,
    QuerySm,
    QuerySmResp,
)

__all__ = [
    # Base classes
    'PDU',
    'TLVParameter',
    'RequestPDU',
    'ResponsePDU',
    'BindRequestPDU',
    'BindResponsePDU',
    'MessagePDU',
    'EmptyBodyPDU',
    # Bind PDUs
    'BindTransmitter',
    'BindTransmitterResp',
    'BindReceiver',
    'BindReceiverResp',
    'BindTransceiver',
    'BindTransceiverResp',
    'Unbind',
    'UnbindResp',
    'Outbind',
    # Message PDUs
    'SubmitSm',
    'SubmitSmResp',
    'DeliverSm',
    'DeliverSmResp',
    # Session PDUs
    'EnquireLink',
    'EnquireLinkResp',
    'GenericNack',
    'AlertNotification',
    'DataSm',
    'DataSmResp',
    'QuerySm',
    'QuerySmResp',
    # Factory functions
    'create_pdu',
    'create_request_pdu',
    'create_response_pdu',
    'create_error_response',
    'decode_pdu',
    'get_pdu_class',
    'get_pdu_name',
    'is_command_supported',
    'create_bind_pdu',
    'create_submit_sm_pdu',
    'create_enquire_link_pdu',
    'create_generic_nack_pdu',
    'PDU_CLASSES',
]
