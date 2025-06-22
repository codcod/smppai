#!/usr/bin/env python3
"""
Example: SMPP Server with Graceful Shutdown

This example demonstrates how to run an SMPP server with graceful shutdown
handling. The server will properly disconnect all clients when receiving
SIGTERM or SIGINT signals.

Usage:
    python examples/graceful_server.py

To test graceful shutdown:
    1. Run the server
    2. Connect clients (see client.py example)
    3. Send SIGTERM or press Ctrl+C
    4. Observe graceful disconnection in logs
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add src to path for running from examples directory
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from smpp.server import SMPPServer


def setup_logging():
    """Set up logging to see server events"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%H:%M:%S'
    )


async def main():
    setup_logging()

    # Create server with custom settings
    server = SMPPServer(
        host='localhost',
        port=2776,  # Use different port to avoid conflicts
        system_id='TestSMSC',
        max_connections=10
    )

    # Configure shutdown timeout
    server.set_shutdown_timeout(15.0)  # 15 seconds max for graceful shutdown

    # Set up event handlers
    def on_client_connected(server_instance, session):
        logging.info(f'Client connected from {session.connection.host}')

    def on_client_bound(server_instance, session):
        logging.info(f'Client bound: {session.system_id} as {session.bind_type}')

    def on_client_disconnected(server_instance, session):
        logging.info(f'Client disconnected: {session.system_id}')

    def on_message_received(server_instance, session, submit_sm):
        logging.info(f'Message: {submit_sm.source_addr} -> {submit_sm.destination_addr}: {submit_sm.short_message.decode("utf-8", errors="ignore")}')
        return f'MSG_{server_instance._message_id_counter:06d}'

    server.on_client_connected = on_client_connected
    server.on_client_bound = on_client_bound
    server.on_client_disconnected = on_client_disconnected
    server.on_message_received = on_message_received

    try:
        # Start server and wait for shutdown signal
        logging.info('Starting SMPP server with graceful shutdown support...')
        logging.info('Press Ctrl+C or send SIGTERM to gracefully shutdown')
        await server.serve_forever()

    except Exception as e:
        logging.error(f'Server error: {e}')
        raise

    logging.info('Server shutdown complete')


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('\nShutdown interrupted by user')
    except Exception as e:
        print(f'Error: {e}')
        sys.exit(1)
