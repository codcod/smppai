"""
SMPP AI - Async SMPP Protocol v3.4 Implementation

A comprehensive, async implementation of the SMPP (Short Message Peer-to-Peer) protocol v3.4
in Python, built with modern asyncio patterns and designed for high performance and maintainability.

This package provides:
- Complete SMPP v3.4 protocol implementation
- Async SMPP client (ESME) for connecting to SMSC servers
- Async SMPP server (SMSC) for handling multiple client connections
- Comprehensive PDU encoding/decoding with validation
- Event-driven message handling and delivery receipts
- Configurable connection management and reconnection
- TLV optional parameter support
- Unicode and multi-part message handling

Quick Start:
    import smpp

    async with smpp.connect("localhost", 2775, "test_client", "password") as client:
        result = await client.send("+306900000000", "Hello World!", sender="ACME")
        print(result.message_ids)

The low-level SMPPClient stays available (and as `client.raw`); smpp.Server
wraps SMPPServer the same way (as `server.raw`).
"""

# Main client and server classes
from .client import (
    Address,
    BindType,
    Client,
    DeliveryReceipt,
    Message,
    SendResult,
    SMPPClient,
    connect,
)

# Exception classes
from .exceptions import (
    SMPPAuthenticationException,
    SMPPBindException,
    SMPPConnectionException,
    SMPPException,
    SMPPInvalidStateException,
    SMPPMessageException,
    SMPPPDUException,
    SMPPProtocolException,
    SMPPThrottlingException,
    SMPPTimeoutException,
    SMPPValidationException,
)

# Protocol constants and enums
from .protocol import (
    CommandId,
    CommandStatus,
    DataCoding,
    EsmClass,
    InterfaceVersion,
    MessageState,
    NpiType,
    OptionalTag,
    PriorityFlag,
    RegisteredDelivery,
    ReplaceIfPresentFlag,
    TonType,
    get_error_message,
    get_request_command_id,
    get_response_command_id,
    is_response_command,
)

# PDU classes and factory functions
from .protocol.pdu import (  # Bind PDUs; Message PDUs; Session PDUs; Factory functions
    PDU,
    BindReceiver,
    BindReceiverResp,
    BindTransceiver,
    BindTransceiverResp,
    BindTransmitter,
    BindTransmitterResp,
    CancelSm,
    CancelSmResp,
    DataSm,
    DataSmResp,
    DeliverSm,
    DeliverSmResp,
    EnquireLink,
    EnquireLinkResp,
    GenericNack,
    Outbind,
    QuerySm,
    QuerySmResp,
    ReplaceSm,
    ReplaceSmResp,
    SubmitSm,
    SubmitSmResp,
    TLVParameter,
    Unbind,
    UnbindResp,
    create_bind_pdu,
    create_pdu,
    create_submit_sm_pdu,
    decode_pdu,
)
from .server import Server, Shutdown, SMPPServer

# Transport layer
from .transport import ConnectionState, SMPPConnection

# GSM functionality
from . import gsm

# Package metadata
__all__ = [
    # Main classes
    'SMPPClient',
    'SMPPServer',
    'BindType',
    # High-level client API
    'connect',
    'Client',
    'Address',
    'SendResult',
    'Message',
    'DeliveryReceipt',
    # High-level server API
    'Server',
    'Shutdown',
    # Protocol constants
    'CommandId',
    'CommandStatus',
    'DataCoding',
    'EsmClass',
    'InterfaceVersion',
    'NpiType',
    'PriorityFlag',
    'RegisteredDelivery',
    'ReplaceIfPresentFlag',
    'TonType',
    'MessageState',
    'OptionalTag',
    'get_error_message',
    'is_response_command',
    'get_response_command_id',
    'get_request_command_id',
    # PDU classes
    'PDU',
    'TLVParameter',
    'BindTransmitter',
    'BindTransmitterResp',
    'BindReceiver',
    'BindReceiverResp',
    'BindTransceiver',
    'BindTransceiverResp',
    'Unbind',
    'UnbindResp',
    'Outbind',
    'SubmitSm',
    'SubmitSmResp',
    'DeliverSm',
    'DeliverSmResp',
    'DataSm',
    'DataSmResp',
    'EnquireLink',
    'EnquireLinkResp',
    'GenericNack',
    'QuerySm',
    'QuerySmResp',
    'CancelSm',
    'CancelSmResp',
    'ReplaceSm',
    'ReplaceSmResp',
    # Factory functions
    'create_pdu',
    'create_bind_pdu',
    'create_submit_sm_pdu',
    'decode_pdu',
    # Exceptions
    'SMPPException',
    'SMPPConnectionException',
    'SMPPPDUException',
    'SMPPTimeoutException',
    'SMPPBindException',
    'SMPPProtocolException',
    'SMPPAuthenticationException',
    'SMPPInvalidStateException',
    'SMPPThrottlingException',
    'SMPPMessageException',
    'SMPPValidationException',
    # Transport
    'SMPPConnection',
    'ConnectionState',
    # GSM functionality
    'gsm',
]


# Convenience imports for common use cases
def create_simple_client(
    host: str, port: int, system_id: str, password: str, **kwargs
) -> SMPPClient:
    """
    Create a simple SMPP client with minimal configuration.

    Args:
        host: SMSC host address
        port: SMSC port number
        system_id: System identifier for authentication
        password: Password for authentication
        **kwargs: Additional configuration options

    Returns:
        Configured SMPPClient instance
    """
    return SMPPClient(
        host=host, port=port, system_id=system_id, password=password, **kwargs
    )


def create_simple_server(
    host: str = 'localhost', port: int = 2775, **kwargs
) -> SMPPServer:
    """
    Create a simple SMPP server with minimal configuration.

    Args:
        host: Server bind address
        port: Server bind port
        **kwargs: Additional configuration options

    Returns:
        Configured SMPPServer instance
    """
    return SMPPServer(host=host, port=port, **kwargs)


# Add convenience functions to __all__
__all__.extend(
    [
        'create_simple_client',
        'create_simple_server',
    ]
)

# Module-level configuration
import logging  # noqa: E402

# Set up default logging to reduce noise unless explicitly configured
logging.getLogger(__name__).addHandler(logging.NullHandler())
