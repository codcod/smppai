#!/usr/bin/env python3
"""
SMPP Server Example

This example demonstrates how to use the SMPP server to accept client connections,
handle bind requests, and process SMS messages.

Updated for the new modular code structure with clean imports from the main smpp package.
"""

import asyncio
import logging
import os
import sys
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from smpp import DataCoding, SMPPServer, SubmitSm
from smpp.server import ClientSession

# Configure logging
logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SMSCServer:
    """Example SMSC server using SMPP"""

    def __init__(self, host: str = 'localhost', port: int = 2775):
        self.server = SMPPServer(
            host=host,
            port=port,
            system_id='TEST_SMSC',
            max_connections=50,
        )

        # Store for received messages
        self.message_store = {}

        # Set up event handlers
        self.server.authenticate = self.authenticate_client
        self.server.on_client_connected = self.handle_client_connected
        self.server.on_client_disconnected = self.handle_client_disconnected
        self.server.on_client_bound = self.handle_client_bound
        self.server.on_message_received = self.handle_message_received

        # Store for message tracking

    def authenticate_client(
        self, system_id: str, password: str, system_type: str
    ) -> bool:
        """Authenticate client credentials"""
        # Simple authentication - in production, use proper credential validation
        valid_clients = {
            'test_client': 'password',
            'test_receiver': 'password',
            'test_transmitter': 'password',
        }

        is_valid = valid_clients.get(system_id) == password

        if is_valid:
            logger.info(f'Authentication successful for {system_id}')
        else:
            logger.warning(f'Authentication failed for {system_id}')

        return is_valid

    def handle_client_connected(
        self, server: SMPPServer, session: ClientSession
    ) -> None:
        """Handle new client connection"""
        logger.info(
            f'Client connected from {session.connection.host}:{session.connection.port}'
        )

    def handle_client_disconnected(
        self, server: SMPPServer, session: ClientSession
    ) -> None:
        """Handle client disconnection"""
        logger.info(f'Client {session.system_id} disconnected')

    def handle_client_bound(self, server: SMPPServer, session: ClientSession) -> None:
        """Handle successful client bind"""
        logger.info(f'Client {session.system_id} bound as {session.bind_type}')

    def handle_message_received(
        self, server: SMPPServer, session: ClientSession, pdu: SubmitSm
    ) -> Optional[str]:
        """Handle SMS message from client"""
        try:
            # Decode message
            message = pdu.short_message.decode('utf-8', errors='ignore')

            logger.info(f'Message received from {session.system_id}:')
            logger.info(f'  From: {pdu.source_addr}')
            logger.info(f'  To: {pdu.destination_addr}')
            logger.info(f'  Message: {message}')
            logger.info(f'  Data Coding: {pdu.data_coding}')

            # Generate custom message ID
            message_id = f'MSG_{session.system_id}_{session.message_counter + 1:06d}'

            # Store message for later delivery or processing
            self.message_store[message_id] = {
                'source': pdu.source_addr,
                'destination': pdu.destination_addr,
                'message': message,
                'client': session.system_id,
                'timestamp': asyncio.get_event_loop().time(),
                'data_coding': pdu.data_coding,
            }

            # Simulate message processing
            asyncio.create_task(self.process_message(message_id, session, pdu))

            return message_id

        except Exception as e:
            logger.error(f'Error handling message: {e}')
            return None

    async def process_message(
        self, message_id: str, session: ClientSession, pdu: SubmitSm
    ) -> None:
        """Process received message (simulate delivery)"""
        try:
            # Simulate processing delay
            await asyncio.sleep(1)

            message_info = self.message_store.get(message_id)
            if not message_info:
                return

            logger.info(f'Processing message {message_id}')

            # Check if this is an echo request
            message = message_info['message'].lower()
            if message.startswith('echo '):
                # Echo the message back
                echo_text = message_info['message'][5:]  # Remove 'echo ' prefix
                await self.send_echo_response(session, pdu, echo_text)

            elif message == 'help':
                # Send help message
                help_text = 'Available commands: ECHO <text>, HELP, STATUS, TIME'
                await self.send_echo_response(session, pdu, help_text)

            elif message == 'status':
                # Send server status
                status_text = (
                    f'Server running. Connected clients: {self.server.client_count}'
                )
                await self.send_echo_response(session, pdu, status_text)

            elif message == 'time':
                # Send current time
                import datetime

                time_text = f'Server time: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
                await self.send_echo_response(session, pdu, time_text)

            # Simulate delivery receipt if requested
            if pdu.registered_delivery:
                await asyncio.sleep(2)  # Simulate delivery delay
                await self.send_delivery_receipt(session, message_id, pdu)

        except Exception as e:
            logger.error(f'Error processing message {message_id}: {e}')

    async def send_echo_response(
        self, session: ClientSession, original_pdu: SubmitSm, response_text: str
    ) -> None:
        """Send an echo response back to the client"""
        try:
            if session.bind_type not in ('receiver', 'transceiver'):
                logger.warning(
                    f'Cannot send response to {session.system_id} - not bound as receiver'
                )
                return

            success = await self.server.deliver_sm(
                target_system_id=session.system_id,
                source_addr=original_pdu.destination_addr,  # Swap addresses
                destination_addr=original_pdu.source_addr,
                short_message=response_text,
                source_addr_ton=original_pdu.dest_addr_ton,
                source_addr_npi=original_pdu.dest_addr_npi,
                dest_addr_ton=original_pdu.source_addr_ton,
                dest_addr_npi=original_pdu.source_addr_npi,
                data_coding=DataCoding.DEFAULT,
            )

            if success:
                logger.info(f'Echo response sent to {session.system_id}')
            else:
                logger.warning(f'Failed to send echo response to {session.system_id}')

        except Exception as e:
            logger.error(f'Error sending echo response: {e}')

    async def send_delivery_receipt(
        self, session: ClientSession, message_id: str, original_pdu: SubmitSm
    ) -> None:
        """Send delivery receipt to client"""
        try:
            if session.bind_type not in ('receiver', 'transceiver'):
                return

            # Create delivery receipt text
            receipt_text = f'id:{message_id} sub:001 dlvrd:001 submit date:2023010112000000 done date:2023010112000100 stat:DELIVRD err:000 text:'

            success = await self.server.deliver_sm(
                target_system_id=session.system_id,
                source_addr=original_pdu.destination_addr,
                destination_addr=original_pdu.source_addr,
                short_message=receipt_text,
                esm_class=0x04,  # Delivery receipt flag
                data_coding=DataCoding.DEFAULT,
            )

            if success:
                logger.info(f'Delivery receipt sent for message {message_id}')
            else:
                logger.warning(
                    f'Failed to send delivery receipt for message {message_id}'
                )

        except Exception as e:
            logger.error(f'Error sending delivery receipt: {e}')

    async def start(self) -> None:
        """Start the SMSC server"""
        await self.server.start()

    async def stop(self) -> None:
        """Stop the SMSC server"""
        await self.server.stop()

    async def broadcast_message(self, source_addr: str, message: str) -> None:
        """Broadcast message to all connected receiver clients"""
        bound_clients = self.server.get_bound_clients()
        receiver_clients = [
            client
            for client in bound_clients
            if client.bind_type in ('receiver', 'transceiver')
        ]

        if not receiver_clients:
            logger.info('No receiver clients to broadcast to')
            return

        logger.info(f'Broadcasting message to {len(receiver_clients)} clients')

        for client in receiver_clients:
            success = await self.server.deliver_sm(
                target_system_id=client.system_id,
                source_addr=source_addr,
                destination_addr='BROADCAST',
                short_message=message,
                data_coding=DataCoding.DEFAULT,
            )

            if success:
                logger.info(f'Broadcast message sent to {client.system_id}')
            else:
                logger.warning(
                    f'Failed to send broadcast message to {client.system_id}'
                )

    def get_server_stats(self) -> dict:
        """Get server statistics"""
        bound_clients = self.server.get_bound_clients()
        return {
            'total_connections': self.server.client_count,
            'bound_clients': len(bound_clients),
            'transmitters': len(
                [c for c in bound_clients if c.bind_type == 'transmitter']
            ),
            'receivers': len([c for c in bound_clients if c.bind_type == 'receiver']),
            'transceivers': len(
                [c for c in bound_clients if c.bind_type == 'transceiver']
            ),
            'total_messages': len(self.message_store),
        }


async def main():
    """Main server function"""
    # Create SMSC server
    smsc = SMSCServer(host='localhost', port=2775)

    try:
        # Start server
        await smsc.start()
        logger.info('SMSC server started. Waiting for connections...')

        # Print server stats periodically
        async def print_stats():
            while True:
                await asyncio.sleep(30)
                stats = smsc.get_server_stats()
                logger.info(f'Server stats: {stats}')

        # Start stats task
        stats_task = asyncio.create_task(print_stats())

        # Simulate broadcast messages periodically
        async def send_broadcasts():
            await asyncio.sleep(60)  # Wait a minute before first broadcast
            counter = 1
            while True:
                await smsc.broadcast_message(
                    source_addr='SYSTEM', message=f'System broadcast message #{counter}'
                )
                counter += 1
                await asyncio.sleep(300)  # Broadcast every 5 minutes

        # Start broadcast task
        broadcast_task = asyncio.create_task(send_broadcasts())

        # Keep server running
        while True:
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        logger.info('Server interrupted by user')
    except Exception as e:
        logger.error(f'Server error: {e}')
    finally:
        # Stop server
        if 'stats_task' in locals():
            stats_task.cancel()
        if 'broadcast_task' in locals():
            broadcast_task.cancel()

        await smsc.stop()
        logger.info('SMSC server stopped')


async def simple_server_example():
    """Simple server example"""
    async with SMPPServer(host='localhost', port=2775) as _server:
        logger.info('Simple SMSC server running...')

        # Keep running until interrupted
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info('Server stopped')


if __name__ == '__main__':
    # Run the main server
    asyncio.run(main())

    # Uncomment to run simple example:
    # asyncio.run(simple_server_example())
