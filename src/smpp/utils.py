"""
SMPP Utilities Module

This module provides basic utility functions and helper classes for SMPP protocol
implementation, including common helper functions and data processing utilities.
"""

import logging
import re
import time
from typing import Optional, Union


def generate_message_id() -> str:
    """Generate a unique message ID."""
    return str(int(time.time() * 1000) % 0x7FFFFFFF)


def normalize_phone_number(phone: str) -> str:
    """Normalize phone number by removing non-digit characters."""
    return re.sub(r'\D', '', phone)


def validate_phone_number(phone: str) -> bool:
    """Basic phone number validation."""
    normalized = normalize_phone_number(phone)
    return len(normalized) >= 7 and len(normalized) <= 15


def is_valid_system_id(system_id: str) -> bool:
    """Validate SMPP system_id."""
    return len(system_id) > 0 and len(system_id) < 16


def mask_sensitive_data(text: str, field_name: str = '') -> str:
    """Mask sensitive data for logging."""
    if 'password' in field_name.lower():
        return '*' * min(len(text), 8) if text else ''
    return text


def setup_logging(level: int = logging.INFO) -> None:
    """Set up basic logging configuration."""
    logging.basicConfig(
        level=level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def calculate_message_length(message: Union[str, bytes]) -> int:
    """Calculate message length."""
    if isinstance(message, str):
        return len(message.encode('utf-8'))
    return len(message)


def format_smpp_time(timestamp: Optional[float] = None) -> str:
    """Format time for SMPP protocol."""
    if timestamp is None:
        timestamp = time.time()
    return time.strftime('%y%m%d%H%M%S000+', time.gmtime(timestamp))


def parse_smpp_time(smpp_time: str) -> Optional[float]:
    """Parse SMPP time string to timestamp."""
    if not smpp_time or len(smpp_time) < 12:
        return None
    try:
        # Parse YYMMDDHHmmss format
        time_part = smpp_time[:12]
        parsed = time.strptime(f'20{time_part}', '%Y%m%d%H%M%S')
        return time.mktime(parsed)
    except ValueError:
        return None


__all__ = [
    # Message processing
    'generate_message_id',
    'calculate_message_length',
    # Phone number handling
    'normalize_phone_number',
    'validate_phone_number',
    # Validation
    'is_valid_system_id',
    # Security
    'mask_sensitive_data',
    # Logging
    'setup_logging',
    # Time handling
    'format_smpp_time',
    'parse_smpp_time',
]
