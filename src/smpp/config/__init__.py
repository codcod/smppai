"""
SMPP Configuration Management

This module provides centralized configuration management for SMPP client and server
implementations, including default values, validation, and environment-based configuration.
"""

from .base import BaseConfig, ClientConfig, ConnectionConfig, ServerConfig
from .defaults import (
    DEFAULT_CLIENT_CONFIG,
    DEFAULT_CONNECTION_CONFIG,
    DEFAULT_LOGGING_CONFIG,
    DEFAULT_SECURITY_CONFIG,
    DEFAULT_SERVER_CONFIG,
    SMPP_PROTOCOL_DEFAULTS,
)
from .settings import (
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
from .validation import (
    ConfigValidator,
    ValidationResult,
    ValidationSeverity,
    validate_config,
)

__all__ = [
    # Base configuration classes
    'BaseConfig',
    'ConnectionConfig',
    'ClientConfig',
    'ServerConfig',
    # Legacy configuration classes
    'SMPPClientConfig',
    'SMPPServerConfig',
    'SecurityConfig',
    'LoggingConfig',
    # Factory functions
    'create_client_config',
    'create_server_config',
    'load_config_from_env',
    'load_config_from_file',
    'create_client_config_from_sources',
    'create_server_config_from_sources',
    # Validation
    'ValidationResult',
    'ValidationSeverity',
    'ConfigValidator',
    'validate_config',
    # Default configurations
    'DEFAULT_CLIENT_CONFIG',
    'DEFAULT_SERVER_CONFIG',
    'DEFAULT_CONNECTION_CONFIG',
    'DEFAULT_SECURITY_CONFIG',
    'DEFAULT_LOGGING_CONFIG',
    'SMPP_PROTOCOL_DEFAULTS',
]
