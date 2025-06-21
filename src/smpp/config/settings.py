"""
SMPP Configuration Settings

This module defines configuration classes and factory functions for SMPP client and server
configurations, providing type-safe and validated configuration management.
"""

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional, Union

from ..exceptions import SMPPValidationException


@dataclass
class ConnectionConfig:
    """Connection-related configuration settings"""

    connect_timeout: float = 30.0
    read_timeout: float = 30.0
    write_timeout: float = 30.0
    enquire_link_interval: float = 60.0
    response_timeout: float = 30.0
    max_reconnect_attempts: int = 3
    reconnect_delay: float = 5.0
    keep_alive: bool = True
    tcp_nodelay: bool = True
    socket_buffer_size: int = 8192

    def validate(self) -> None:
        """Validate connection configuration"""
        if self.connect_timeout <= 0:
            raise SMPPValidationException('connect_timeout must be positive')
        if self.read_timeout <= 0:
            raise SMPPValidationException('read_timeout must be positive')
        if self.write_timeout <= 0:
            raise SMPPValidationException('write_timeout must be positive')
        if self.enquire_link_interval <= 0:
            raise SMPPValidationException('enquire_link_interval must be positive')
        if self.response_timeout <= 0:
            raise SMPPValidationException('response_timeout must be positive')
        if self.max_reconnect_attempts < 0:
            raise SMPPValidationException('max_reconnect_attempts must be non-negative')
        if self.reconnect_delay < 0:
            raise SMPPValidationException('reconnect_delay must be non-negative')


@dataclass
class SecurityConfig:
    """Security-related configuration settings"""

    require_authentication: bool = True
    allowed_system_types: Optional[list] = None
    max_bind_attempts: int = 3
    bind_attempt_window: float = 300.0  # 5 minutes
    password_min_length: int = 0
    password_max_length: int = 8
    enable_encryption: bool = False
    encryption_key: Optional[str] = None
    trusted_sources: Optional[list] = None
    blacklisted_sources: Optional[list] = None

    def validate(self) -> None:
        """Validate security configuration"""
        if self.max_bind_attempts <= 0:
            raise SMPPValidationException('max_bind_attempts must be positive')
        if self.bind_attempt_window <= 0:
            raise SMPPValidationException('bind_attempt_window must be positive')
        if self.password_min_length < 0:
            raise SMPPValidationException('password_min_length must be non-negative')
        if self.password_max_length < self.password_min_length:
            raise SMPPValidationException(
                'password_max_length must be >= password_min_length'
            )
        if self.enable_encryption and not self.encryption_key:
            raise SMPPValidationException(
                'encryption_key required when encryption is enabled'
            )


@dataclass
class LoggingConfig:
    """Logging configuration settings"""

    level: str = 'INFO'
    format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    log_pdus: bool = False
    log_pdu_body: bool = False
    log_file: Optional[str] = None
    max_log_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    enable_console: bool = True

    def validate(self) -> None:
        """Validate logging configuration"""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if self.level.upper() not in valid_levels:
            raise SMPPValidationException(f'Invalid log level: {self.level}')
        if self.max_log_size <= 0:
            raise SMPPValidationException('max_log_size must be positive')
        if self.backup_count < 0:
            raise SMPPValidationException('backup_count must be non-negative')


@dataclass
class SMPPClientConfig:
    """Complete SMPP client configuration"""

    # Connection details
    host: str = 'localhost'
    port: int = 2775

    # Authentication
    system_id: str = ''
    password: str = ''
    system_type: str = ''

    # Protocol settings
    interface_version: int = 0x34
    addr_ton: int = 0
    addr_npi: int = 0
    address_range: str = ''

    # Configuration objects
    connection: ConnectionConfig = field(default_factory=ConnectionConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)

    # Additional settings
    auto_reconnect: bool = True
    bind_mode: str = 'transceiver'  # transmitter, receiver, transceiver
    message_queue_size: int = 1000
    throttle_limit: Optional[int] = None
    throttle_window: float = 1.0

    def validate(self) -> None:
        """Validate complete client configuration"""
        if not self.host:
            raise SMPPValidationException('host cannot be empty')
        if not (1 <= self.port <= 65535):
            raise SMPPValidationException('port must be between 1 and 65535')
        if not self.system_id:
            raise SMPPValidationException('system_id cannot be empty')
        if len(self.system_id) >= 16:
            raise SMPPValidationException('system_id too long (max 15 chars)')
        if len(self.password) >= 9:
            raise SMPPValidationException('password too long (max 8 chars)')
        if len(self.system_type) >= 13:
            raise SMPPValidationException('system_type too long (max 12 chars)')
        if self.interface_version not in (0x33, 0x34):
            raise SMPPValidationException('unsupported interface_version')
        if not (0 <= self.addr_ton <= 255):
            raise SMPPValidationException('addr_ton must be 0-255')
        if not (0 <= self.addr_npi <= 255):
            raise SMPPValidationException('addr_npi must be 0-255')
        if len(self.address_range) >= 41:
            raise SMPPValidationException('address_range too long (max 40 chars)')
        if self.bind_mode not in ('transmitter', 'receiver', 'transceiver'):
            raise SMPPValidationException('invalid bind_mode')
        if self.message_queue_size <= 0:
            raise SMPPValidationException('message_queue_size must be positive')
        if self.throttle_limit is not None and self.throttle_limit <= 0:
            raise SMPPValidationException('throttle_limit must be positive')
        if self.throttle_window <= 0:
            raise SMPPValidationException('throttle_window must be positive')

        # Validate nested configurations
        self.connection.validate()
        self.security.validate()
        self.logging.validate()


@dataclass
class SMPPServerConfig:
    """Complete SMPP server configuration"""

    # Server settings
    host: str = 'localhost'
    port: int = 2775
    system_id: str = 'SMSC'

    # Protocol settings
    interface_version: int = 0x34
    max_connections: int = 100
    max_sessions_per_ip: int = 10

    # Configuration objects
    connection: ConnectionConfig = field(default_factory=ConnectionConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)

    # Server-specific settings
    enable_delivery_receipts: bool = True
    message_retention_hours: int = 24
    throughput_limit: Optional[int] = None  # messages per second
    enable_load_balancing: bool = False
    health_check_interval: float = 30.0

    def validate(self) -> None:
        """Validate complete server configuration"""
        if not self.host:
            raise SMPPValidationException('host cannot be empty')
        if not (1 <= self.port <= 65535):
            raise SMPPValidationException('port must be between 1 and 65535')
        if not self.system_id:
            raise SMPPValidationException('system_id cannot be empty')
        if len(self.system_id) >= 16:
            raise SMPPValidationException('system_id too long (max 15 chars)')
        if self.interface_version not in (0x33, 0x34):
            raise SMPPValidationException('unsupported interface_version')
        if self.max_connections <= 0:
            raise SMPPValidationException('max_connections must be positive')
        if self.max_sessions_per_ip <= 0:
            raise SMPPValidationException('max_sessions_per_ip must be positive')
        if self.message_retention_hours < 0:
            raise SMPPValidationException(
                'message_retention_hours must be non-negative'
            )
        if self.throughput_limit is not None and self.throughput_limit <= 0:
            raise SMPPValidationException('throughput_limit must be positive')
        if self.health_check_interval <= 0:
            raise SMPPValidationException('health_check_interval must be positive')

        # Validate nested configurations
        self.connection.validate()
        self.security.validate()
        self.logging.validate()


def create_client_config(**kwargs) -> SMPPClientConfig:
    """
    Create a validated SMPP client configuration.

    Args:
        **kwargs: Configuration parameters

    Returns:
        Validated SMPPClientConfig instance

    Raises:
        SMPPValidationException: If configuration is invalid
    """
    config = SMPPClientConfig(**kwargs)
    config.validate()
    return config


def create_server_config(**kwargs) -> SMPPServerConfig:
    """
    Create a validated SMPP server configuration.

    Args:
        **kwargs: Configuration parameters

    Returns:
        Validated SMPPServerConfig instance

    Raises:
        SMPPValidationException: If configuration is invalid
    """
    config = SMPPServerConfig(**kwargs)
    config.validate()
    return config


def load_config_from_env(prefix: str = 'SMPP_') -> Dict[str, Any]:
    """
    Load configuration from environment variables.

    Args:
        prefix: Environment variable prefix

    Returns:
        Dictionary of configuration values
    """
    config: Dict[str, Any] = {}

    # Define environment variable mappings
    env_mappings = {
        f'{prefix}HOST': 'host',
        f'{prefix}PORT': ('port', int),
        f'{prefix}SYSTEM_ID': 'system_id',
        f'{prefix}PASSWORD': 'password',
        f'{prefix}SYSTEM_TYPE': 'system_type',
        f'{prefix}INTERFACE_VERSION': ('interface_version', lambda x: int(x, 16)),
        f'{prefix}ADDR_TON': ('addr_ton', int),
        f'{prefix}ADDR_NPI': ('addr_npi', int),
        f'{prefix}ADDRESS_RANGE': 'address_range',
        f'{prefix}BIND_MODE': 'bind_mode',
        f'{prefix}AUTO_RECONNECT': (
            'auto_reconnect',
            lambda x: x.lower() in ('true', '1', 'yes'),
        ),
        f'{prefix}CONNECT_TIMEOUT': ('connection.connect_timeout', float),
        f'{prefix}READ_TIMEOUT': ('connection.read_timeout', float),
        f'{prefix}WRITE_TIMEOUT': ('connection.write_timeout', float),
        f'{prefix}ENQUIRE_LINK_INTERVAL': ('connection.enquire_link_interval', float),
        f'{prefix}RESPONSE_TIMEOUT': ('connection.response_timeout', float),
        f'{prefix}MAX_RECONNECT_ATTEMPTS': ('connection.max_reconnect_attempts', int),
        f'{prefix}RECONNECT_DELAY': ('connection.reconnect_delay', float),
        f'{prefix}LOG_LEVEL': 'logging.level',
        f'{prefix}LOG_FILE': 'logging.log_file',
        f'{prefix}LOG_PDUS': (
            'logging.log_pdus',
            lambda x: x.lower() in ('true', '1', 'yes'),
        ),
    }

    for env_var, mapping in env_mappings.items():
        value = os.getenv(env_var)
        if value is not None:
            if isinstance(mapping, tuple):
                key, converter = mapping
                try:
                    value = converter(value)
                except (ValueError, TypeError) as e:
                    raise SMPPValidationException(f'Invalid value for {env_var}: {e}')
            else:
                key = mapping

            # Handle nested configuration
            if '.' in key:
                parts = key.split('.')
                current = config
                for part in parts[:-1]:
                    if part not in current:
                        current[part] = {}
                    current_part = current[part]
                    if not isinstance(current_part, dict):
                        current[part] = {}
                        current_part = current[part]
                    current = current_part
                current[parts[-1]] = value
            else:
                config[key] = value

    return config


def load_config_from_file(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Load configuration from JSON file.

    Args:
        file_path: Path to configuration file

    Returns:
        Dictionary of configuration values

    Raises:
        SMPPValidationException: If file cannot be read or parsed
    """
    try:
        path = Path(file_path)
        if not path.exists():
            raise SMPPValidationException(f'Configuration file not found: {file_path}')

        with open(path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        if not isinstance(config, dict):
            raise SMPPValidationException(
                'Configuration file must contain a JSON object'
            )

        return config

    except json.JSONDecodeError as e:
        raise SMPPValidationException(f'Invalid JSON in configuration file: {e}')
    except IOError as e:
        raise SMPPValidationException(f'Error reading configuration file: {e}')


def merge_configurations(*configs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge multiple configuration dictionaries.
    Later configurations override earlier ones.

    Args:
        *configs: Configuration dictionaries to merge

    Returns:
        Merged configuration dictionary
    """
    result: Dict[str, Any] = {}

    for config in configs:
        if not isinstance(config, dict):
            continue

        for key, value in config.items():
            if (
                isinstance(value, dict)
                and key in result
                and isinstance(result[key], dict)
            ):
                result[key] = merge_configurations(result[key], value)
            else:
                result[key] = value

    return result


def create_client_config_from_sources(
    file_path: Optional[Union[str, Path]] = None,
    env_prefix: str = 'SMPP_CLIENT_',
    **overrides,
) -> SMPPClientConfig:
    """
    Create client configuration from multiple sources.

    Priority order (highest to lowest):
    1. Keyword overrides
    2. Environment variables
    3. Configuration file
    4. Defaults

    Args:
        file_path: Optional configuration file path
        env_prefix: Environment variable prefix
        **overrides: Direct configuration overrides

    Returns:
        Validated SMPPClientConfig instance
    """
    configs = []

    # Load from file if provided
    if file_path:
        configs.append(load_config_from_file(file_path))

    # Load from environment
    configs.append(load_config_from_env(env_prefix))

    # Add overrides
    if overrides:
        configs.append(overrides)

    # Merge all configurations
    merged_config = merge_configurations(*configs)

    # Handle nested configurations
    if 'connection' in merged_config:
        connection_config = ConnectionConfig(**merged_config.pop('connection'))
        merged_config['connection'] = connection_config

    if 'security' in merged_config:
        security_config = SecurityConfig(**merged_config.pop('security'))
        merged_config['security'] = security_config

    if 'logging' in merged_config:
        logging_config = LoggingConfig(**merged_config.pop('logging'))
        merged_config['logging'] = logging_config

    return create_client_config(**merged_config)


def create_server_config_from_sources(
    file_path: Optional[Union[str, Path]] = None,
    env_prefix: str = 'SMPP_SERVER_',
    **overrides,
) -> SMPPServerConfig:
    """
    Create server configuration from multiple sources.

    Priority order (highest to lowest):
    1. Keyword overrides
    2. Environment variables
    3. Configuration file
    4. Defaults

    Args:
        file_path: Optional configuration file path
        env_prefix: Environment variable prefix
        **overrides: Direct configuration overrides

    Returns:
        Validated SMPPServerConfig instance
    """
    configs = []

    # Load from file if provided
    if file_path:
        configs.append(load_config_from_file(file_path))

    # Load from environment
    configs.append(load_config_from_env(env_prefix))

    # Add overrides
    if overrides:
        configs.append(overrides)

    # Merge all configurations
    merged_config = merge_configurations(*configs)

    # Handle nested configurations
    if 'connection' in merged_config:
        connection_config = ConnectionConfig(**merged_config.pop('connection'))
        merged_config['connection'] = connection_config

    if 'security' in merged_config:
        security_config = SecurityConfig(**merged_config.pop('security'))
        merged_config['security'] = security_config

    if 'logging' in merged_config:
        logging_config = LoggingConfig(**merged_config.pop('logging'))
        merged_config['logging'] = logging_config

    return create_server_config(**merged_config)
