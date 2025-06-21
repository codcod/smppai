"""
SMPP Configuration Defaults

This module provides default configuration values for SMPP client and server
implementations, ensuring consistent behavior across the library.
"""

from .settings import (
    ConnectionConfig,
    LoggingConfig,
    SecurityConfig,
    SMPPClientConfig,
    SMPPServerConfig,
)

# Default connection configuration
DEFAULT_CONNECTION_CONFIG = ConnectionConfig(
    connect_timeout=30.0,
    read_timeout=30.0,
    write_timeout=30.0,
    enquire_link_interval=60.0,
    response_timeout=30.0,
    max_reconnect_attempts=3,
    reconnect_delay=5.0,
    keep_alive=True,
    tcp_nodelay=True,
    socket_buffer_size=8192,
)

# Default security configuration
DEFAULT_SECURITY_CONFIG = SecurityConfig(
    require_authentication=True,
    allowed_system_types=None,
    max_bind_attempts=3,
    bind_attempt_window=300.0,
    password_min_length=0,
    password_max_length=8,
    enable_encryption=False,
    encryption_key=None,
    trusted_sources=None,
    blacklisted_sources=None,
)

# Default logging configuration
DEFAULT_LOGGING_CONFIG = LoggingConfig(
    level='INFO',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    log_pdus=False,
    log_pdu_body=False,
    log_file=None,
    max_log_size=10 * 1024 * 1024,  # 10MB
    backup_count=5,
    enable_console=True,
)

# Default client configuration
DEFAULT_CLIENT_CONFIG = SMPPClientConfig(
    host='localhost',
    port=2775,
    system_id='test_client',
    password='password',
    system_type='',
    interface_version=0x34,
    addr_ton=0,
    addr_npi=0,
    address_range='',
    connection=DEFAULT_CONNECTION_CONFIG,
    security=DEFAULT_SECURITY_CONFIG,
    logging=DEFAULT_LOGGING_CONFIG,
    auto_reconnect=True,
    bind_mode='transceiver',
    message_queue_size=1000,
    throttle_limit=None,
    throttle_window=1.0,
)

# Default server configuration
DEFAULT_SERVER_CONFIG = SMPPServerConfig(
    host='localhost',
    port=2775,
    system_id='SMSC',
    interface_version=0x34,
    max_connections=100,
    max_sessions_per_ip=10,
    connection=DEFAULT_CONNECTION_CONFIG,
    security=DEFAULT_SECURITY_CONFIG,
    logging=DEFAULT_LOGGING_CONFIG,
    enable_delivery_receipts=True,
    message_retention_hours=24,
    throughput_limit=None,
    enable_load_balancing=False,
    health_check_interval=30.0,
)

# SMPP protocol-specific defaults
SMPP_PROTOCOL_DEFAULTS = {
    # Field lengths (including null terminator)
    'MAX_SYSTEM_ID_LENGTH': 16,
    'MAX_PASSWORD_LENGTH': 9,
    'MAX_SYSTEM_TYPE_LENGTH': 13,
    'MAX_ADDRESS_RANGE_LENGTH': 41,
    'MAX_ADDRESS_LENGTH': 21,
    'MAX_SERVICE_TYPE_LENGTH': 6,
    'MAX_SHORT_MESSAGE_LENGTH': 255,
    # PDU structure
    'PDU_HEADER_SIZE': 16,
    'MAX_PDU_SIZE': 65536,
    # Default field values
    'DEFAULT_SYSTEM_TYPE': '',
    'DEFAULT_INTERFACE_VERSION': 0x34,
    'DEFAULT_ADDR_TON': 0,
    'DEFAULT_ADDR_NPI': 0,
    'DEFAULT_SERVICE_TYPE': '',
    'DEFAULT_ESM_CLASS': 0,
    'DEFAULT_PROTOCOL_ID': 0,
    'DEFAULT_PRIORITY_FLAG': 0,
    'DEFAULT_SCHEDULE_DELIVERY_TIME': '',
    'DEFAULT_VALIDITY_PERIOD': '',
    'DEFAULT_REGISTERED_DELIVERY': 0,
    'DEFAULT_REPLACE_IF_PRESENT_FLAG': 0,
    'DEFAULT_DATA_CODING': 0,
    'DEFAULT_SM_DEFAULT_MSG_ID': 0,
    # Timing defaults
    'DEFAULT_BIND_TIMEOUT': 30.0,
    'DEFAULT_ENQUIRE_LINK_INTERVAL': 60.0,
    'DEFAULT_RESPONSE_TIMEOUT': 30.0,
    'DEFAULT_CONNECTION_TIMEOUT': 30.0,
    # Quality of Service
    'DEFAULT_WINDOW_SIZE': 100,
    'DEFAULT_SESSION_INIT_TIMER': 10000,  # milliseconds
    'DEFAULT_ENQUIRE_LINK_TIMER': 60000,  # milliseconds
    'DEFAULT_INACTIVITY_TIMER': 300000,  # milliseconds
    # Message handling
    'DEFAULT_MESSAGE_QUEUE_SIZE': 1000,
    'DEFAULT_MAX_MESSAGE_PARTS': 10,
    'DEFAULT_DELIVERY_RECEIPT_FORMAT': 'id:{msg_id} sub:001 dlvrd:001 submit date:{submit_date} done date:{done_date} stat:{message_state} err:000 text:{message_text}',
    # Connection limits
    'DEFAULT_MAX_CONNECTIONS': 100,
    'DEFAULT_MAX_SESSIONS_PER_IP': 10,
    'DEFAULT_CONNECTION_POOL_SIZE': 10,
    # Retry and backoff
    'DEFAULT_MAX_RETRY_ATTEMPTS': 3,
    'DEFAULT_RETRY_DELAY': 1.0,
    'DEFAULT_BACKOFF_MULTIPLIER': 2.0,
    'DEFAULT_MAX_BACKOFF_DELAY': 60.0,
    # Throttling
    'DEFAULT_THROTTLE_WINDOW': 1.0,
    'DEFAULT_THROTTLE_LIMIT': None,
    'DEFAULT_SUBMIT_SM_THROTTLE': 10,  # messages per second
    'DEFAULT_DELIVER_SM_THROTTLE': 50,  # messages per second
    # Health checks
    'DEFAULT_HEALTH_CHECK_INTERVAL': 30.0,
    'DEFAULT_HEALTH_CHECK_TIMEOUT': 5.0,
    'DEFAULT_HEALTH_CHECK_RETRIES': 3,
    # Logging
    'DEFAULT_LOG_LEVEL': 'INFO',
    'DEFAULT_LOG_FORMAT': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'DEFAULT_MAX_LOG_SIZE': 10 * 1024 * 1024,  # 10MB
    'DEFAULT_LOG_BACKUP_COUNT': 5,
}

# Environment variable defaults
ENV_VAR_DEFAULTS = {
    'SMPP_HOST': 'localhost',
    'SMPP_PORT': '2775',
    'SMPP_SYSTEM_ID': 'test_client',
    'SMPP_PASSWORD': 'password',
    'SMPP_SYSTEM_TYPE': '',
    'SMPP_INTERFACE_VERSION': '0x34',
    'SMPP_BIND_MODE': 'transceiver',
    'SMPP_AUTO_RECONNECT': 'true',
    'SMPP_LOG_LEVEL': 'INFO',
    'SMPP_LOG_PDUS': 'false',
    'SMPP_CONNECT_TIMEOUT': '30.0',
    'SMPP_READ_TIMEOUT': '30.0',
    'SMPP_WRITE_TIMEOUT': '30.0',
    'SMPP_ENQUIRE_LINK_INTERVAL': '60.0',
    'SMPP_RESPONSE_TIMEOUT': '30.0',
    'SMPP_MAX_RECONNECT_ATTEMPTS': '3',
    'SMPP_RECONNECT_DELAY': '5.0',
}

# Server-specific environment variable defaults
SERVER_ENV_VAR_DEFAULTS = {
    'SMPP_SERVER_HOST': 'localhost',
    'SMPP_SERVER_PORT': '2775',
    'SMPP_SERVER_SYSTEM_ID': 'SMSC',
    'SMPP_SERVER_MAX_CONNECTIONS': '100',
    'SMPP_SERVER_MAX_SESSIONS_PER_IP': '10',
    'SMPP_SERVER_ENABLE_DELIVERY_RECEIPTS': 'true',
    'SMPP_SERVER_MESSAGE_RETENTION_HOURS': '24',
    'SMPP_SERVER_HEALTH_CHECK_INTERVAL': '30.0',
}

# Configuration validation rules
VALIDATION_RULES = {
    'host': {
        'required': True,
        'type': str,
        'min_length': 1,
        'max_length': 255,
    },
    'port': {
        'required': True,
        'type': int,
        'min_value': 1,
        'max_value': 65535,
    },
    'system_id': {
        'required': True,
        'type': str,
        'min_length': 1,
        'max_length': 15,
        'pattern': r'^[a-zA-Z0-9_]+$',
    },
    'password': {
        'required': False,
        'type': str,
        'max_length': 8,
    },
    'system_type': {
        'required': False,
        'type': str,
        'max_length': 12,
    },
    'interface_version': {
        'required': True,
        'type': int,
        'allowed_values': [0x33, 0x34],
    },
    'addr_ton': {
        'required': True,
        'type': int,
        'min_value': 0,
        'max_value': 255,
    },
    'addr_npi': {
        'required': True,
        'type': int,
        'min_value': 0,
        'max_value': 255,
    },
    'connect_timeout': {
        'required': True,
        'type': float,
        'min_value': 0.1,
        'max_value': 300.0,
    },
    'read_timeout': {
        'required': True,
        'type': float,
        'min_value': 0.1,
        'max_value': 300.0,
    },
    'write_timeout': {
        'required': True,
        'type': float,
        'min_value': 0.1,
        'max_value': 300.0,
    },
    'enquire_link_interval': {
        'required': True,
        'type': float,
        'min_value': 1.0,
        'max_value': 3600.0,
    },
    'response_timeout': {
        'required': True,
        'type': float,
        'min_value': 0.1,
        'max_value': 300.0,
    },
}

# Message type defaults
MESSAGE_TYPE_DEFAULTS = {
    'SMS': {
        'service_type': '',
        'source_addr_ton': 0,
        'source_addr_npi': 0,
        'dest_addr_ton': 0,
        'dest_addr_npi': 0,
        'esm_class': 0,
        'protocol_id': 0,
        'priority_flag': 0,
        'registered_delivery': 0,
        'replace_if_present_flag': 0,
        'data_coding': 0,
        'sm_default_msg_id': 0,
    },
    'DELIVERY_RECEIPT': {
        'service_type': '',
        'source_addr_ton': 0,
        'source_addr_npi': 0,
        'dest_addr_ton': 0,
        'dest_addr_npi': 0,
        'esm_class': 4,  # Delivery receipt
        'protocol_id': 0,
        'priority_flag': 0,
        'registered_delivery': 0,
        'replace_if_present_flag': 0,
        'data_coding': 0,
        'sm_default_msg_id': 0,
    },
}

# TLV parameter defaults
TLV_DEFAULTS = {
    'SAR_MSG_REF_NUM': 0x020C,
    'SAR_TOTAL_SEGMENTS': 0x020E,
    'SAR_SEGMENT_SEQNUM': 0x020F,
    'MESSAGE_PAYLOAD': 0x0424,
    'RECEIPTED_MESSAGE_ID': 0x001E,
    'MESSAGE_STATE': 0x0427,
    'NETWORK_ERROR_CODE': 0x0423,
    'SOURCE_PORT': 0x020A,
    'DESTINATION_PORT': 0x020B,
}
