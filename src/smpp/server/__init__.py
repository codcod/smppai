"""
SMPP Server Module

This module provides a comprehensive async SMPP server implementation
for creating SMSC-like services that can handle multiple client connections,
authenticate clients, route messages, and provide delivery receipts.

The module includes:
- SMPPServer: Main server class with full SMSC functionality
- Multi-client session management
- Message routing and delivery
- Authentication and authorization
- Configurable for testing and production use
"""

from .server import ClientSession, SMPPServer

__all__ = [
    # Main server class
    'SMPPServer',
    'ClientSession',
]
