"""
SMPP PDU Factory

This module provides factory functions for creating and managing PDU instances
based on command IDs, enabling centralized PDU creation and registration.
"""

from typing import Any, Dict, Optional, Type, TypeVar, cast

from ...exceptions import SMPPPDUException
from ..constants import CommandId
from .base import PDU
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

# Add type variable for better type safety
T_PDU = TypeVar('T_PDU', bound=PDU)

# Mapping of command IDs to PDU classes
PDU_CLASSES: Dict[int, Type[PDU]] = {
    # Bind operations
    CommandId.BIND_TRANSMITTER: BindTransmitter,
    CommandId.BIND_TRANSMITTER_RESP: BindTransmitterResp,
    CommandId.BIND_RECEIVER: BindReceiver,
    CommandId.BIND_RECEIVER_RESP: BindReceiverResp,
    CommandId.BIND_TRANSCEIVER: BindTransceiver,
    CommandId.BIND_TRANSCEIVER_RESP: BindTransceiverResp,
    CommandId.UNBIND: Unbind,
    CommandId.UNBIND_RESP: UnbindResp,
    CommandId.OUTBIND: Outbind,
    # Message operations
    CommandId.SUBMIT_SM: SubmitSm,
    CommandId.SUBMIT_SM_RESP: SubmitSmResp,
    CommandId.DELIVER_SM: DeliverSm,
    CommandId.DELIVER_SM_RESP: DeliverSmResp,
    # Session management
    CommandId.ENQUIRE_LINK: EnquireLink,
    CommandId.ENQUIRE_LINK_RESP: EnquireLinkResp,
    CommandId.GENERIC_NACK: GenericNack,
    # Extended operations
    CommandId.ALERT_NOTIFICATION: AlertNotification,
    CommandId.DATA_SM: DataSm,
    CommandId.DATA_SM_RESP: DataSmResp,
    CommandId.QUERY_SM: QuerySm,
    CommandId.QUERY_SM_RESP: QuerySmResp,
}


def get_pdu_class(command_id: int) -> Type[PDU]:
    """Get PDU class for a given command ID.

    Args:
        command_id: SMPP command ID

    Returns:
        Type[PDU]: PDU class type

    Raises:
        SMPPPDUException: If command ID is not supported
    """
    pdu_class = PDU_CLASSES.get(command_id)
    if pdu_class is None:
        raise SMPPPDUException(
            f'Unknown command ID: 0x{command_id:08X}',
            command_id=command_id,
            error_code='UNKNOWN_COMMAND_ID',
        )
    return pdu_class


def create_pdu(command_id: int, **kwargs: Any) -> PDU:
    """Factory function to create PDU instances.

    Args:
        command_id: SMPP command ID
        **kwargs: PDU-specific parameters

    Returns:
        PDU: PDU instance

    Raises:
        SMPPPDUException: If command ID is not supported or creation fails
    """
    pdu_class = get_pdu_class(command_id)
    try:
        return pdu_class(command_id=command_id, **kwargs)
    except TypeError as e:
        raise SMPPPDUException(
            f'Failed to create PDU: {e}',
            command_id=command_id,
            pdu_type=pdu_class.__name__,
            error_code='PDU_CREATION_FAILED',
        ) from e


def create_typed_pdu(pdu_type: Type[T_PDU], command_id: int, **kwargs: Any) -> T_PDU:
    """Create a PDU with specific type for better type safety.

    Args:
        pdu_type: Expected PDU class type
        command_id: SMPP command ID
        **kwargs: PDU-specific parameters

    Returns:
        T_PDU: Typed PDU instance

    Raises:
        SMPPPDUException: If command ID doesn't match expected type or creation fails
    """
    pdu_class = get_pdu_class(command_id)
    if pdu_class != pdu_type:
        raise SMPPPDUException(
            f'Command ID 0x{command_id:08X} does not match expected type {pdu_type.__name__}',
            command_id=command_id,
            pdu_type=pdu_class.__name__,
            error_code='TYPE_MISMATCH',
        )

    return cast(T_PDU, create_pdu(command_id, **kwargs))


def create_request_pdu(command_id: int, **kwargs) -> PDU:
    """Create a request PDU, ensuring it's not a response command ID.

    Args:
        command_id: SMPP command ID (must be request)
        **kwargs: PDU-specific parameters

    Returns:
        PDU: Request PDU instance

    Raises:
        SMPPPDUException: If command ID is a response or not supported
    """
    if command_id & 0x80000000:
        raise SMPPPDUException(
            f'Command ID 0x{command_id:08X} is a response, not a request'
        )

    return create_pdu(command_id, **kwargs)


def create_response_pdu(
    request_command_id: int, sequence_number: int, command_status: int = 0, **kwargs
) -> PDU:
    """Create a response PDU for a given request command ID.

    Args:
        request_command_id: Original request command ID
        sequence_number: Sequence number from request
        command_status: Response status code (default: 0)
        **kwargs: PDU-specific parameters

    Returns:
        PDU: Response PDU instance

    Raises:
        SMPPPDUException: If response PDU cannot be created
    """
    if request_command_id & 0x80000000:
        raise SMPPPDUException(
            f'Command ID 0x{request_command_id:08X} is already a response'
        )

    response_command_id = request_command_id | 0x80000000

    return create_pdu(
        response_command_id,
        sequence_number=sequence_number,
        command_status=command_status,
        **kwargs,
    )


def create_error_response(
    request_pdu: PDU, error_status: int, error_message: Optional[str] = None
) -> PDU:
    """
    Create an error response PDU for a request PDU.

    Args:
        request_pdu: Original request PDU
        error_status: Error status code
        error_message: Optional error message

    Returns:
        Error response PDU

    Raises:
        SMPPPDUException: If error response cannot be created
    """
    if request_pdu.is_response():
        raise SMPPPDUException('Cannot create error response for response PDU')

    try:
        response_pdu = create_response_pdu(
            request_pdu.command_id, request_pdu.sequence_number, error_status
        )

        if error_message:
            # Add error message as optional parameter if supported
            response_pdu.add_optional_parameter(0x001D, error_message.encode('utf-8'))

        return response_pdu

    except SMPPPDUException:
        # If specific response PDU cannot be created, use GenericNack
        return GenericNack(
            sequence_number=request_pdu.sequence_number, command_status=error_status
        )


def decode_pdu(data: bytes) -> PDU:
    """
    Decode PDU from bytes using the factory.

    Args:
        data: Raw PDU bytes

    Returns:
        Decoded PDU instance

    Raises:
        SMPPPDUException: If PDU cannot be decoded
    """
    return PDU.decode(data)


def is_command_supported(command_id: int) -> bool:
    """
    Check if a command ID is supported.

    Args:
        command_id: SMPP command ID

    Returns:
        True if command is supported, False otherwise
    """
    return command_id in PDU_CLASSES


def get_pdu_name(command_id: int) -> str:
    """
    Get the name of the PDU class for a command ID.

    Args:
        command_id: SMPP command ID

    Returns:
        PDU class name

    Raises:
        SMPPPDUException: If command ID is not supported
    """
    pdu_class = get_pdu_class(command_id)
    return pdu_class.__name__


def create_bind_pdu(
    bind_type: str,
    system_id: str,
    password: str,
    system_type: str = '',
    interface_version: int = 0x34,
    addr_ton: int = 0,
    addr_npi: int = 0,
    address_range: str = '',
) -> PDU:
    """
    Create a bind PDU of the specified type.

    Args:
        bind_type: Type of bind ('transmitter', 'receiver', 'transceiver')
        system_id: System identifier
        password: Authentication password
        system_type: System type
        interface_version: SMPP interface version
        addr_ton: Address Type of Number
        addr_npi: Address Numbering Plan Indicator
        address_range: Address range

    Returns:
        Bind PDU instance

    Raises:
        SMPPPDUException: If bind type is invalid
    """
    bind_type = bind_type.lower()

    if bind_type == 'transmitter':
        command_id = CommandId.BIND_TRANSMITTER
    elif bind_type == 'receiver':
        command_id = CommandId.BIND_RECEIVER
    elif bind_type == 'transceiver':
        command_id = CommandId.BIND_TRANSCEIVER
    else:
        raise SMPPPDUException(f'Invalid bind type: {bind_type}')

    return create_pdu(
        command_id,
        system_id=system_id,
        password=password,
        system_type=system_type,
        interface_version=interface_version,
        addr_ton=addr_ton,
        addr_npi=addr_npi,
        address_range=address_range,
    )


def create_submit_sm_pdu(
    source_addr: str,
    destination_addr: str,
    short_message: bytes,
    service_type: str = '',
    source_addr_ton: int = 0,
    source_addr_npi: int = 0,
    dest_addr_ton: int = 0,
    dest_addr_npi: int = 0,
    esm_class: int = 0,
    protocol_id: int = 0,
    priority_flag: int = 0,
    schedule_delivery_time: str = '',
    validity_period: str = '',
    registered_delivery: int = 0,
    replace_if_present_flag: int = 0,
    data_coding: int = 0,
    sm_default_msg_id: int = 0,
) -> SubmitSm:
    """Create a submit_sm PDU with common parameters.

    Args:
        source_addr: Source address
        destination_addr: Destination address
        short_message: Message content as bytes
        service_type: Service type (default: '')
        source_addr_ton: Source address TON (default: 0)
        source_addr_npi: Source address NPI (default: 0)
        dest_addr_ton: Destination address TON (default: 0)
        dest_addr_npi: Destination address NPI (default: 0)
        esm_class: ESM class (default: 0)
        protocol_id: Protocol ID (default: 0)
        priority_flag: Priority flag (default: 0)
        schedule_delivery_time: Scheduled delivery time (default: '')
        validity_period: Validity period (default: '')
        registered_delivery: Registered delivery (default: 0)
        replace_if_present_flag: Replace if present flag (default: 0)
        data_coding: Data coding (default: 0)
        sm_default_msg_id: SM default message ID (default: 0)

    Returns:
        SubmitSm: SubmitSm PDU instance
    """
    pdu = create_pdu(
        CommandId.SUBMIT_SM,
        service_type=service_type,
        source_addr_ton=source_addr_ton,
        source_addr_npi=source_addr_npi,
        source_addr=source_addr,
        dest_addr_ton=dest_addr_ton,
        dest_addr_npi=dest_addr_npi,
        destination_addr=destination_addr,
        esm_class=esm_class,
        protocol_id=protocol_id,
        priority_flag=priority_flag,
        schedule_delivery_time=schedule_delivery_time,
        validity_period=validity_period,
        registered_delivery=registered_delivery,
        replace_if_present_flag=replace_if_present_flag,
        data_coding=data_coding,
        sm_default_msg_id=sm_default_msg_id,
        short_message=short_message,
    )
    # Type checker needs this cast
    assert isinstance(pdu, SubmitSm)
    return pdu


def create_enquire_link_pdu() -> EnquireLink:
    """Create an enquire_link PDU.

    Returns:
        EnquireLink: EnquireLink PDU instance
    """
    pdu = create_pdu(CommandId.ENQUIRE_LINK)
    # Type checker needs this cast
    assert isinstance(pdu, EnquireLink)
    return pdu


def create_generic_nack_pdu(sequence_number: int, command_status: int) -> GenericNack:
    """Create a generic_nack PDU.

    Args:
        sequence_number: Sequence number from invalid PDU
        command_status: Error status code

    Returns:
        GenericNack: GenericNack PDU instance
    """
    pdu = create_pdu(
        CommandId.GENERIC_NACK,
        sequence_number=sequence_number,
        command_status=command_status,
    )
    # Type checker needs this cast
    assert isinstance(pdu, GenericNack)
    return pdu
