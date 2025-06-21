"""Configuration validation utilities for SMPP library."""

import re
from enum import Enum
from ipaddress import AddressValueError, IPv4Address, IPv6Address
from typing import Any, Dict, List, Optional, Union

from ..exceptions import SMPPConfigurationException, SMPPErrorCode


class ValidationSeverity(Enum):
    """Validation severity levels."""

    ERROR = 'error'
    WARNING = 'warning'
    INFO = 'info'


class ValidationResult:
    """Result of configuration validation."""

    def __init__(
        self,
        is_valid: bool = True,
        errors: Optional[List[str]] = None,
        warnings: Optional[List[str]] = None,
    ):
        self.is_valid = is_valid
        self.errors = errors or []
        self.warnings = warnings or []

    def add_error(self, message: str) -> None:
        """Add validation error."""
        self.errors.append(message)
        self.is_valid = False

    def add_warning(self, message: str) -> None:
        """Add validation warning."""
        self.warnings.append(message)

    def merge(self, other: 'ValidationResult') -> None:
        """Merge another validation result."""
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        if not other.is_valid:
            self.is_valid = False


class ConfigValidator:
    """Configuration validator with comprehensive validation rules."""

    # Port ranges
    MIN_PORT = 1
    MAX_PORT = 65535

    # Timeout ranges (seconds)
    MIN_TIMEOUT = 0.1
    MAX_TIMEOUT = 3600.0

    # System ID patterns
    SYSTEM_ID_PATTERN = re.compile(r'^[a-zA-Z0-9_-]{1,16}$')

    # Address patterns
    PHONE_NUMBER_PATTERN = re.compile(r'^\+?[1-9]\d{1,15}$')
    SHORT_CODE_PATTERN = re.compile(r'^\d{3,8}$')

    @classmethod
    def validate_host(cls, host: str) -> ValidationResult:
        """Validate host address."""
        result = ValidationResult()

        if not host or not host.strip():
            result.add_error('Host cannot be empty')
            return result

        host = host.strip()

        # Check if it's an IP address
        try:
            IPv4Address(host)
            return result
        except AddressValueError:
            pass

        try:
            IPv6Address(host)
            return result
        except AddressValueError:
            pass

        # Check if it's a valid hostname
        if not cls._is_valid_hostname(host):
            result.add_error(f'Invalid hostname format: {host}')

        return result

    @classmethod
    def validate_port(cls, port: int) -> ValidationResult:
        """Validate port number."""
        result = ValidationResult()

        if not isinstance(port, int):
            result.add_error('Port must be an integer')
            return result

        if port < cls.MIN_PORT or port > cls.MAX_PORT:
            result.add_error(f'Port must be between {cls.MIN_PORT} and {cls.MAX_PORT}')
        elif port < 1024:
            result.add_warning('Using privileged port (< 1024)')

        return result

    @classmethod
    def validate_timeout(
        cls, timeout: float, name: str = 'timeout'
    ) -> ValidationResult:
        """Validate timeout value."""
        result = ValidationResult()

        if not isinstance(timeout, (int, float)):
            result.add_error(f'{name} must be a number')
            return result

        if timeout < cls.MIN_TIMEOUT or timeout > cls.MAX_TIMEOUT:
            result.add_error(
                f'{name} must be between {cls.MIN_TIMEOUT} and {cls.MAX_TIMEOUT} seconds'
            )
        elif timeout > 300:  # 5 minutes
            result.add_warning(f'Long {name} ({timeout}s) may cause connection issues')

        return result

    @classmethod
    def validate_system_id(cls, system_id: str) -> ValidationResult:
        """Validate system ID."""
        result = ValidationResult()

        if not system_id:
            result.add_error('System ID cannot be empty')
            return result

        if not cls.SYSTEM_ID_PATTERN.match(system_id):
            result.add_error(
                'System ID must be 1-16 characters, alphanumeric, underscore, or hyphen'
            )

        return result

    @classmethod
    def validate_password(cls, password: str) -> ValidationResult:
        """Validate password."""
        result = ValidationResult()

        if not password:
            result.add_warning('Empty password - consider using authentication')
            return result

        if len(password) > 9:
            result.add_error('Password cannot exceed 9 characters')

        if len(password) < 4:
            result.add_warning('Short password may be insecure')

        return result

    @classmethod
    def validate_phone_number(cls, phone_number: str) -> ValidationResult:
        """Validate phone number format."""
        result = ValidationResult()

        if not phone_number:
            result.add_error('Phone number cannot be empty')
            return result

        # Check for short code
        if cls.SHORT_CODE_PATTERN.match(phone_number):
            return result

        # Check for regular phone number
        if not cls.PHONE_NUMBER_PATTERN.match(phone_number):
            result.add_error(f'Invalid phone number format: {phone_number}')

        return result

    @classmethod
    def validate_message_length(
        cls, message: Union[str, bytes], encoding: str = 'default'
    ) -> ValidationResult:
        """Validate message length based on encoding."""
        result = ValidationResult()

        if isinstance(message, str):
            message_bytes = message.encode('utf-8')
        else:
            message_bytes = message

        # Standard SMS limits
        if encoding.lower() in ('default', 'ascii', 'latin1'):
            max_length = 160
            if len(message_bytes) > max_length:
                result.add_error(
                    f'Message too long: {len(message_bytes)} > {max_length}'
                )
        elif encoding.lower() in ('ucs2', 'utf-16'):
            max_length = 70
            char_count = len(
                message.decode('utf-8') if isinstance(message, bytes) else message
            )
            if char_count > max_length:
                result.add_error(
                    f'Unicode message too long: {char_count} > {max_length}'
                )

        return result

    @classmethod
    def validate_connection_config(
        cls, config_dict: Dict[str, Any]
    ) -> ValidationResult:
        """Validate connection configuration."""
        result = ValidationResult()

        # Required fields
        required_fields = ['host', 'port']
        for field in required_fields:
            if field not in config_dict:
                result.add_error(f'Missing required field: {field}')

        # Validate individual fields
        if 'host' in config_dict:
            host_result = cls.validate_host(config_dict['host'])
            result.merge(host_result)

        if 'port' in config_dict:
            port_result = cls.validate_port(config_dict['port'])
            result.merge(port_result)

        # Validate timeout fields
        timeout_fields = [
            'connect_timeout',
            'bind_timeout',
            'enquire_link_timeout',
            'response_timeout',
            'socket_timeout',
        ]

        for field in timeout_fields:
            if field in config_dict:
                timeout_result = cls.validate_timeout(config_dict[field], field)
                result.merge(timeout_result)

        return result

    @classmethod
    def validate_client_config(cls, config_dict: Dict[str, Any]) -> ValidationResult:
        """Validate client configuration."""
        result = ValidationResult()

        # Validate connection config
        conn_result = cls.validate_connection_config(config_dict)
        result.merge(conn_result)

        # Required client fields
        required_fields = ['system_id', 'password']
        for field in required_fields:
            if field not in config_dict:
                result.add_error(f'Missing required field: {field}')

        # Validate individual fields
        if 'system_id' in config_dict:
            system_id_result = cls.validate_system_id(config_dict['system_id'])
            result.merge(system_id_result)

        if 'password' in config_dict:
            password_result = cls.validate_password(config_dict['password'])
            result.merge(password_result)

        # Validate numeric fields
        numeric_fields = {
            'window_size': (1, 1000),
            'enquire_link_interval': (10, 3600),
            'max_reconnect_attempts': (0, 100),
            'reconnect_delay': (1, 300),
        }

        for field, (min_val, max_val) in numeric_fields.items():
            if field in config_dict:
                value = config_dict[field]
                if not isinstance(value, int) or value < min_val or value > max_val:
                    result.add_error(
                        f'{field} must be an integer between {min_val} and {max_val}'
                    )

        return result

    @classmethod
    def validate_server_config(cls, config_dict: Dict[str, Any]) -> ValidationResult:
        """Validate server configuration."""
        result = ValidationResult()

        # Validate connection config
        conn_result = cls.validate_connection_config(config_dict)
        result.merge(conn_result)

        # Validate server-specific fields
        if 'max_connections' in config_dict:
            max_conn = config_dict['max_connections']
            if not isinstance(max_conn, int) or max_conn < 1 or max_conn > 10000:
                result.add_error('max_connections must be between 1 and 10000')

        if 'backlog' in config_dict:
            backlog = config_dict['backlog']
            if not isinstance(backlog, int) or backlog < 1 or backlog > 1000:
                result.add_error('backlog must be between 1 and 1000')

        return result

    @classmethod
    def _is_valid_hostname(cls, hostname: str) -> bool:
        """Check if hostname is valid."""
        if len(hostname) > 255:
            return False

        if hostname[-1] == '.':
            hostname = hostname[:-1]

        allowed = re.compile(r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$')

        return all(allowed.match(part) for part in hostname.split('.'))


def validate_config(
    config_dict: Dict[str, Any], config_type: str = 'client'
) -> ValidationResult:
    """Validate configuration dictionary.

    Args:
        config_dict: Configuration to validate
        config_type: Type of configuration ("client", "server", "connection")

    Returns:
        ValidationResult with errors and warnings

    Raises:
        SMPPConfigurationException: If config_type is invalid
    """
    validator_map = {
        'client': ConfigValidator.validate_client_config,
        'server': ConfigValidator.validate_server_config,
        'connection': ConfigValidator.validate_connection_config,
    }

    validator = validator_map.get(config_type)
    if not validator:
        raise SMPPConfigurationException(
            f'Invalid config type: {config_type}',
            error_code=SMPPErrorCode.INVALID_PARAMETER,
        )

    return validator(config_dict)
