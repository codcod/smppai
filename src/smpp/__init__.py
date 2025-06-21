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
    from smpp import SMPPClient, create_client_config

    config = create_client_config(
        host="localhost",
        port=2775,
        system_id="test_client",
        password="password"
    )

    async with SMPPClient(config) as client:
        await client.bind_transceiver()
        message_id = await client.submit_sm(
            source_addr="1234",
            destination_addr="5678",
            short_message="Hello World!"
        )
"""

# Main client and server classes
from .client import BindType, SMPPClient

# Configuration management
from .config import (
    ConnectionConfig,
    LoggingConfig,
    SecurityConfig,
    SMPPClientConfig,
    SMPPServerConfig,
    create_client_config,
    create_client_config_from_sources,
    create_server_config,
    create_server_config_from_sources,
    load_config_from_env,
    load_config_from_file,
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
    DeliverSm,
    DeliverSmResp,
    EnquireLink,
    EnquireLinkResp,
    GenericNack,
    Outbind,
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
from .server import SMPPServer

# Transport layer
from .transport import ConnectionState, SMPPConnection

# Package metadata
__all__ = [
    # Main classes
    'SMPPClient',
    'SMPPServer',
    'BindType',
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
    'EnquireLink',
    'EnquireLinkResp',
    'GenericNack',
    # Factory functions
    'create_pdu',
    'create_bind_pdu',
    'create_submit_sm_pdu',
    'decode_pdu',
    # Configuration
    'SMPPClientConfig',
    'SMPPServerConfig',
    'ConnectionConfig',
    'SecurityConfig',
    'LoggingConfig',
    'create_client_config',
    'create_server_config',
    'load_config_from_env',
    'load_config_from_file',
    'create_client_config_from_sources',
    'create_server_config_from_sources',
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
    config = create_client_config(
        host=host, port=port, system_id=system_id, password=password, **kwargs
    )
    return SMPPClient(
        host=config.host,
        port=config.port,
        system_id=config.system_id,
        password=config.password,
        **{
            k: getattr(config, k)
            for k in vars(config)
            if k not in ('host', 'port', 'system_id', 'password')
        },
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
    config = create_server_config(host=host, port=port, **kwargs)
    return SMPPServer(
        host=config.host,
        port=config.port,
        **{k: getattr(config, k) for k in vars(config) if k not in ('host', 'port')},
    )


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
