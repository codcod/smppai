"""
SMPP Transport Layer

This module provides the transport layer abstraction for SMPP connections,
including async TCP connection handling, connection state management,
and low-level protocol communication.
"""

from .connection import ConnectionState, SMPPConnection

__all__ = [
    # Connection classes
    'SMPPConnection',
    'ConnectionState',
]
