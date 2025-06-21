"""
SMPP Configuration Base Classes

This module provides base configuration classes with validation and serialization
for the SMPP library components.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Type, TypeVar, Union

from ..exceptions import SMPPValidationException

T = TypeVar('T', bound='BaseConfig')


@dataclass
class BaseConfig:
    """Base configuration class with validation and serialization."""

    def validate(self) -> None:
        """Validate configuration values. Override in subclasses."""
        pass

    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """Create config from dictionary with type conversion."""
        # Filter data to only include fields that exist in the dataclass
        field_names = {f.name for f in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in field_names}

        try:
            instance = cls(**filtered_data)
            instance.validate()
            return instance
        except (TypeError, ValueError) as e:
            raise SMPPValidationException(
                f'Invalid configuration data for {cls.__name__}: {e}',
                field_name='config_data',
                validation_rule='type_conversion',
                original_error=e,
            ) from e

    @classmethod
    def from_env(cls: Type[T], prefix: str = '') -> T:
        """Create config from environment variables."""
        env_data: Dict[str, Any] = {}
        prefix = prefix.upper()

        for field_name, field_info in cls.__dataclass_fields__.items():
            env_key = f'{prefix}{field_name.upper()}'
            env_value = os.getenv(env_key)

            if env_value is not None:
                # Type conversion based on field type
                field_type = field_info.type
                try:
                    if field_type is bool:
                        env_data[field_name] = env_value.lower() in (
                            'true',
                            '1',
                            'yes',
                            'on',
                        )
                    elif field_type is int:
                        env_data[field_name] = int(env_value)
                    elif field_type is float:
                        env_data[field_name] = float(env_value)
                    else:
                        env_data[field_name] = env_value
                except (ValueError, TypeError) as e:
                    raise SMPPValidationException(
                        f'Invalid environment value for {env_key}: {env_value}',
                        field_name=field_name,
                        field_value=env_value,
                        validation_rule='env_type_conversion',
                        original_error=e,
                    ) from e

        return cls.from_dict(env_data)

    @classmethod
    def from_file(cls: Type[T], file_path: Union[str, Path]) -> T:
        """Create config from JSON file."""
        file_path = Path(file_path)

        if not file_path.exists():
            raise SMPPValidationException(
                f'Configuration file not found: {file_path}',
                field_name='config_file',
                field_value=str(file_path),
                validation_rule='file_exists',
            )

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise SMPPValidationException(
                f'Invalid JSON in configuration file: {file_path}',
                field_name='config_file',
                field_value=str(file_path),
                validation_rule='valid_json',
                original_error=e,
            ) from e
        except OSError as e:
            raise SMPPValidationException(
                f'Error reading configuration file: {file_path}',
                field_name='config_file',
                field_value=str(file_path),
                validation_rule='file_readable',
                original_error=e,
            ) from e

        return cls.from_dict(data)

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        result = {}
        for field_name, field_value in self.__dict__.items():
            if isinstance(field_value, BaseConfig):
                result[field_name] = field_value.to_dict()
            else:
                result[field_name] = field_value
        return result

    def to_file(self, file_path: Union[str, Path]) -> None:
        """Save config to JSON file."""
        file_path = Path(file_path)

        try:
            # Ensure directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=2, default=str)
        except OSError as e:
            raise SMPPValidationException(
                f'Error writing configuration file: {file_path}',
                field_name='config_file',
                field_value=str(file_path),
                validation_rule='file_writable',
                original_error=e,
            ) from e


class ConnectionConfig(BaseConfig):
    """Configuration for SMPP connections."""

    host: str = 'localhost'
    port: int = 2775
    timeout: float = 30.0
    keep_alive: bool = True
    max_retries: int = 3
    retry_delay: float = 1.0
    max_pending_pdus: int = 1000
    cleanup_interval: float = 300.0

    def validate(self) -> None:
        """Validate connection configuration."""
        if not self.host:
            raise SMPPValidationException(
                'Host cannot be empty',
                field_name='host',
                field_value=self.host,
                validation_rule='non_empty',
            )

        if not (1 <= self.port <= 65535):
            raise SMPPValidationException(
                f'Invalid port: {self.port} (must be 1-65535)',
                field_name='port',
                field_value=str(self.port),
                validation_rule='port_range',
            )

        if self.timeout <= 0:
            raise SMPPValidationException(
                f'Invalid timeout: {self.timeout} (must be > 0)',
                field_name='timeout',
                field_value=str(self.timeout),
                validation_rule='positive_number',
            )

        if self.max_retries < 0:
            raise SMPPValidationException(
                f'Invalid max_retries: {self.max_retries} (must be >= 0)',
                field_name='max_retries',
                field_value=str(self.max_retries),
                validation_rule='non_negative',
            )

        if self.retry_delay < 0:
            raise SMPPValidationException(
                f'Invalid retry_delay: {self.retry_delay} (must be >= 0)',
                field_name='retry_delay',
                field_value=str(self.retry_delay),
                validation_rule='non_negative',
            )

        if self.max_pending_pdus <= 0:
            raise SMPPValidationException(
                f'Invalid max_pending_pdus: {self.max_pending_pdus} (must be > 0)',
                field_name='max_pending_pdus',
                field_value=str(self.max_pending_pdus),
                validation_rule='positive_number',
            )

        if self.cleanup_interval <= 0:
            raise SMPPValidationException(
                f'Invalid cleanup_interval: {self.cleanup_interval} (must be > 0)',
                field_name='cleanup_interval',
                field_value=str(self.cleanup_interval),
                validation_rule='positive_number',
            )


class ClientConfig(BaseConfig):
    """Configuration for SMPP clients."""

    system_id: str = ''
    password: str = ''
    system_type: str = ''
    interface_version: int = 0x34
    addr_ton: int = 0
    addr_npi: int = 0
    address_range: str = ''
    bind_timeout: float = 30.0
    enquire_link_interval: float = 60.0
    response_timeout: float = 30.0
    connection: ConnectionConfig = field(default_factory=ConnectionConfig)

    def validate(self) -> None:
        """Validate client configuration."""
        if not self.system_id:
            raise SMPPValidationException(
                'System ID is required',
                field_name='system_id',
                field_value=self.system_id,
                validation_rule='required',
            )

        if len(self.system_id) > 16:
            raise SMPPValidationException(
                f'System ID too long: {len(self.system_id)} > 16',
                field_name='system_id',
                field_value=self.system_id,
                validation_rule='max_length',
            )

        if len(self.password) > 9:
            raise SMPPValidationException(
                f'Password too long: {len(self.password)} > 9',
                field_name='password',
                field_value='***',  # Don't log actual password
                validation_rule='max_length',
            )

        if len(self.system_type) > 13:
            raise SMPPValidationException(
                f'System type too long: {len(self.system_type)} > 13',
                field_name='system_type',
                field_value=self.system_type,
                validation_rule='max_length',
            )

        if self.interface_version not in (0x33, 0x34):
            raise SMPPValidationException(
                f'Unsupported interface version: 0x{self.interface_version:02X}',
                field_name='interface_version',
                field_value=f'0x{self.interface_version:02X}',
                validation_rule='supported_version',
            )

        if not (0 <= self.addr_ton <= 255):
            raise SMPPValidationException(
                f'Invalid addr_ton: {self.addr_ton} (must be 0-255)',
                field_name='addr_ton',
                field_value=str(self.addr_ton),
                validation_rule='byte_range',
            )

        if not (0 <= self.addr_npi <= 255):
            raise SMPPValidationException(
                f'Invalid addr_npi: {self.addr_npi} (must be 0-255)',
                field_name='addr_npi',
                field_value=str(self.addr_npi),
                validation_rule='byte_range',
            )

        if len(self.address_range) > 41:
            raise SMPPValidationException(
                f'Address range too long: {len(self.address_range)} > 41',
                field_name='address_range',
                field_value=self.address_range,
                validation_rule='max_length',
            )

        if self.bind_timeout <= 0:
            raise SMPPValidationException(
                f'Invalid bind_timeout: {self.bind_timeout} (must be > 0)',
                field_name='bind_timeout',
                field_value=str(self.bind_timeout),
                validation_rule='positive_number',
            )

        if self.enquire_link_interval <= 0:
            raise SMPPValidationException(
                f'Invalid enquire_link_interval: {self.enquire_link_interval} (must be > 0)',
                field_name='enquire_link_interval',
                field_value=str(self.enquire_link_interval),
                validation_rule='positive_number',
            )

        if self.response_timeout <= 0:
            raise SMPPValidationException(
                f'Invalid response_timeout: {self.response_timeout} (must be > 0)',
                field_name='response_timeout',
                field_value=str(self.response_timeout),
                validation_rule='positive_number',
            )

        # Validate nested connection config
        self.connection.validate()


class ServerConfig(BaseConfig):
    """Configuration for SMPP servers."""

    host: str = '0.0.0.0'
    port: int = 2775
    system_id: str = 'SMPP_SERVER'
    max_connections: int = 100
    bind_timeout: float = 30.0
    response_timeout: float = 30.0
    enquire_link_timeout: float = 300.0
    connection: ConnectionConfig = field(default_factory=ConnectionConfig)

    def validate(self) -> None:
        """Validate server configuration."""
        if not self.host:
            raise SMPPValidationException(
                'Host cannot be empty',
                field_name='host',
                field_value=self.host,
                validation_rule='non_empty',
            )

        if not (1 <= self.port <= 65535):
            raise SMPPValidationException(
                f'Invalid port: {self.port} (must be 1-65535)',
                field_name='port',
                field_value=str(self.port),
                validation_rule='port_range',
            )

        if not self.system_id:
            raise SMPPValidationException(
                'System ID is required',
                field_name='system_id',
                field_value=self.system_id,
                validation_rule='required',
            )

        if len(self.system_id) > 16:
            raise SMPPValidationException(
                f'System ID too long: {len(self.system_id)} > 16',
                field_name='system_id',
                field_value=self.system_id,
                validation_rule='max_length',
            )

        if self.max_connections <= 0:
            raise SMPPValidationException(
                f'Invalid max_connections: {self.max_connections} (must be > 0)',
                field_name='max_connections',
                field_value=str(self.max_connections),
                validation_rule='positive_number',
            )

        if self.bind_timeout <= 0:
            raise SMPPValidationException(
                f'Invalid bind_timeout: {self.bind_timeout} (must be > 0)',
                field_name='bind_timeout',
                field_value=str(self.bind_timeout),
                validation_rule='positive_number',
            )

        if self.response_timeout <= 0:
            raise SMPPValidationException(
                f'Invalid response_timeout: {self.response_timeout} (must be > 0)',
                field_name='response_timeout',
                field_value=str(self.response_timeout),
                validation_rule='positive_number',
            )

        if self.enquire_link_timeout <= 0:
            raise SMPPValidationException(
                f'Invalid enquire_link_timeout: {self.enquire_link_timeout} (must be > 0)',
                field_name='enquire_link_timeout',
                field_value=str(self.enquire_link_timeout),
                validation_rule='positive_number',
            )

        # Validate nested connection config
        self.connection.validate()
