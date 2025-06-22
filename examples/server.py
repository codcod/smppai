#!/usr/bin/env python3
"""
SMPP Server Example

This example demonstrates how to use the SMPP server with enhanced shutdown features
to accept client connections, handle bind requests, and process SMS messages.

Enhanced Shutdown Features:
- Graceful notification to bound clients
- Configurable grace periods and timeouts
- Automatic unbind sequence
- Comprehensive logging of shutdown process

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

# Configure logging with enhanced format for shutdown monitoring
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)-8s] [%(name)s] %(message)s',
    datefmt='%H:%M:%S',
)
logger = logging.getLogger(__name__)


class SMSCServer:
    """
    Example SMSC server using SMPP with enhanced shutdown capabilities.

    Features:
    - Enhanced shutdown with client notifications and grace periods
    - Message processing with echo commands
    - Broadcast messaging capabilities
    - Delivery receipt simulation
    - Comprehensive client authentication
    """

    def __init__(
        self, host: str = 'localhost', port: int = 2775
    ):  # Changed to high port number
        # Initialize server with enhanced shutdown enabled
        self.server = SMPPServer(
            host=host,
            port=port,
            system_id='SMSC',  # Fixed: SMPP system_id must be <= 16 characters
            max_connections=50,
            setup_signal_handlers=True,  # Enable signal-based shutdown
        )

        # Message storage and state
        self.message_store = {}
        self._shutdown_requested = False
        self._background_tasks: set[asyncio.Task] = set()
        self._cleanup_lock = asyncio.Lock()

        # Configure enhanced shutdown parameters
        self._configure_enhanced_shutdown()

        # Set up event handlers
        self._setup_event_handlers()

    def _configure_enhanced_shutdown(self) -> None:
        """Configure enhanced shutdown with reasonable timeouts for demonstration."""
        try:
            # Use the new configure_shutdown method for all parameters at once
            self.server.configure_shutdown(
                grace_period=15.0,  # Give clients 15 seconds to disconnect gracefully
                reminder_delay=5.0,  # Send reminder after 5 more seconds
                shutdown_timeout=10.0,  # Force disconnect after 10 additional seconds
            )

            logger.info('Enhanced shutdown configuration applied successfully')

            # Log the current configuration for visibility
            config = self.server.get_shutdown_config()
            logger.info('Shutdown configuration:')
            for key, value in config.items():
                logger.info(f'  {key}: {value}')

        except ValueError as e:
            logger.error(f'Failed to configure shutdown: {e}')
            # Fall back to individual configuration if needed
            logger.info('Using individual shutdown configuration methods as fallback')
            self.server.set_shutdown_grace_period(15.0)
            self.server.set_shutdown_reminder_delay(5.0)
            self.server.set_shutdown_timeout(10.0)

    def _setup_event_handlers(self) -> None:
        """Set up all server event handlers."""
        self.server.authenticate = self.authenticate_client
        self.server.on_client_connected = self.handle_client_connected
        self.server.on_client_disconnected = self.handle_client_disconnected
        self.server.on_client_bound = self.handle_client_bound
        self.server.on_message_received = self.handle_message_received

    def authenticate_client(
        self, system_id: str, password: str, system_type: str
    ) -> bool:
        """
        Authenticate client credentials with enhanced logging.

        Args:
            system_id: Client system identifier
            password: Client password
            system_type: Client system type

        Returns:
            True if authentication successful, False otherwise
        """
        # Enhanced client credentials for demonstration (SMPP passwords must be <= 8 chars)
        valid_clients = {
            'test_client': 'password',
            'test_receiver': 'password',
            'test_transmitter': 'password',
            'demo_client': 'demo_pas',
            'demo_client_1': 'demo123',  # For shutdown demo
            'demo_client_2': 'demo123',  # For shutdown demo
            'demo_client_3': 'demo123',  # For shutdown demo
            'shutdown_test': 'shutdown',  # Special client for shutdown testing
            # Integration test clients
            'client_0': 'password',
            'client_1': 'password',
            'client_2': 'password',
            'client_3': 'password',
            'client_4': 'password',
        }

        is_valid = valid_clients.get(system_id) == password

        if is_valid:
            logger.info(
                f'✓ Authentication successful for {system_id} (type: {system_type})'
            )
        else:
            logger.warning(
                f'✗ Authentication failed for {system_id} (type: {system_type})'
            )

        return is_valid

    def handle_client_connected(
        self, server: SMPPServer, session: ClientSession
    ) -> None:
        """Handle new client connection with enhanced logging."""
        client_info = f'{session.connection.host}:{session.connection.port}'
        logger.info(f'🔗 New client connected from {client_info}')

        # Log current connection count
        logger.info(f'📊 Total active connections: {server.client_count}')

    def handle_client_disconnected(
        self, server: SMPPServer, session: ClientSession
    ) -> None:
        """Handle client disconnection with enhanced logging."""
        logger.info(f'🔌 Client {session.system_id or "unknown"} disconnected')
        logger.info(f'📊 Total active connections: {server.client_count}')

    def handle_client_bound(self, server: SMPPServer, session: ClientSession) -> None:
        """Handle successful client bind with enhanced logging."""
        logger.info(f'🔐 Client {session.system_id} bound as {session.bind_type}')

        # Send welcome message to clients that can receive
        if session.bind_type in ('receiver', 'transceiver'):
            asyncio.create_task(self._send_welcome_message(session))

    def handle_message_received(
        self, server: SMPPServer, session: ClientSession, pdu: SubmitSm
    ) -> Optional[str]:
        """Handle SMS message from client with enhanced logging and commands."""
        try:
            # Decode message
            message = pdu.short_message.decode('utf-8', errors='ignore')

            logger.info(f'📥 Message received from {session.system_id}:')
            logger.info(f'   From: {pdu.source_addr} → To: {pdu.destination_addr}')
            logger.info(f'   Content: "{message}"')
            logger.info(f'   Data Coding: {pdu.data_coding}')

            # Generate custom message ID
            message_id = f'MSG_{session.system_id}_{session.message_counter + 1:06d}'

            # Store message for later processing
            self.message_store[message_id] = {
                'source': pdu.source_addr,
                'destination': pdu.destination_addr,
                'message': message,
                'client': session.system_id,
                'timestamp': asyncio.get_event_loop().time(),
                'data_coding': pdu.data_coding,
            }

            # Process message asynchronously
            task = asyncio.create_task(self.process_message(message_id, session, pdu))
            self._background_tasks.add(task)
            task.add_done_callback(self._background_tasks.discard)

            return message_id

        except Exception as e:
            logger.error(f'❌ Error handling message: {e}')
            return None

    async def process_message(
        self, message_id: str, session: ClientSession, pdu: SubmitSm
    ) -> None:
        """Process received message with enhanced command support."""
        try:
            # Simulate processing delay
            await asyncio.sleep(0.5)

            message_info = self.message_store.get(message_id)
            if not message_info:
                return

            logger.info(f'⚙️  Processing message {message_id}')

            # Enhanced command processing
            message = message_info['message'].lower().strip()

            if message.startswith('echo '):
                # Echo the message back
                echo_text = message_info['message'][5:]  # Remove 'echo ' prefix
                await self._send_response(session, pdu, echo_text)

            elif message == 'help':
                # Send enhanced help message (shortened to fit SMS limits)
                help_text = (
                    'Commands: ECHO <text>, HELP, STATUS, TIME, SHUTDOWN, CLIENTS'
                )
                await self._send_response(session, pdu, help_text)

            elif message == 'status':
                # Send enhanced server status
                stats = self.get_server_stats()
                status_text = (
                    f'Server Status:\n'
                    f'Total connections: {stats["total_connections"]}\n'
                    f'Bound clients: {stats["bound_clients"]}\n'
                    f'Total messages: {stats["total_messages"]}\n'
                    f'Shutdown requested: {self._shutdown_requested}'
                )
                await self._send_response(session, pdu, status_text)

            elif message == 'time':
                # Send current time
                import datetime

                time_text = f'Server time: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
                await self._send_response(session, pdu, time_text)

            elif message == 'clients':
                # List connected clients
                bound_clients = self.server.get_bound_clients()
                if bound_clients:
                    client_list = '\n'.join(
                        [
                            f'{client.system_id} ({client.bind_type})'
                            for client in bound_clients
                        ]
                    )
                    clients_text = f'Connected clients:\n{client_list}'
                else:
                    clients_text = 'No bound clients'
                await self._send_response(session, pdu, clients_text)

            elif message == 'shutdown':
                # Demonstrate enhanced shutdown
                await self._demonstrate_shutdown(session, pdu)

            # Simulate delivery receipt if requested
            if pdu.registered_delivery:
                await asyncio.sleep(1.0)  # Simulate delivery delay
                await self._send_delivery_receipt(session, message_id, pdu)

        except Exception as e:
            logger.error(f'❌ Error processing message {message_id}: {e}')

    async def _send_response(
        self, session: ClientSession, original_pdu: SubmitSm, response_text: str
    ) -> None:
        """Send a response back to the client."""
        try:
            if session.bind_type not in ('receiver', 'transceiver'):
                logger.warning(
                    f'⚠️  Cannot send response to {session.system_id} - not bound as receiver'
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
                logger.info(f'📤 Response sent to {session.system_id}')
            else:
                logger.warning(f'⚠️  Failed to send response to {session.system_id}')

        except Exception as e:
            logger.error(f'❌ Error sending response: {e}')

    async def _demonstrate_shutdown(
        self, session: ClientSession, original_pdu: SubmitSm
    ) -> None:
        """Demonstrate the enhanced shutdown feature."""
        try:
            demo_text = (
                f'Enhanced shutdown demo initiated by {session.system_id}!\n'
                'Watch the logs for:\n'
                '1. Shutdown notifications to all clients\n'
                '2. Grace period countdown\n'
                '3. Reminder messages\n'
                '4. Unbind sequence\n'
                '5. Force disconnect\n'
                'Server will shut down in 10 seconds...'
            )

            await self._send_response(session, original_pdu, demo_text)

            # Broadcast shutdown demo announcement
            await self.broadcast_message(
                source_addr='SYSTEM',
                message='DEMO: Enhanced shutdown will begin in 10 seconds!',
            )

            # Schedule shutdown after delay
            async def delayed_shutdown():
                await asyncio.sleep(10)
                logger.info('🛑 Demo shutdown initiated by client command')
                self._shutdown_requested = True
                # Trigger shutdown via the server's shutdown event
                self.server._shutdown_event.set()

            task = asyncio.create_task(delayed_shutdown())
            self._background_tasks.add(task)
            task.add_done_callback(self._background_tasks.discard)

        except Exception as e:
            logger.error(f'❌ Error in shutdown demonstration: {e}')

    async def _send_delivery_receipt(
        self, session: ClientSession, message_id: str, original_pdu: SubmitSm
    ) -> None:
        """Send delivery receipt to client."""
        try:
            if session.bind_type not in ('receiver', 'transceiver'):
                return

            # Create delivery receipt text
            receipt_text = (
                f'id:{message_id} sub:001 dlvrd:001 '
                f'submit date:2025010112000000 done date:2025010112000100 '
                f'stat:DELIVRD err:000 text:'
            )

            success = await self.server.deliver_sm(
                target_system_id=session.system_id,
                source_addr=original_pdu.destination_addr,
                destination_addr=original_pdu.source_addr,
                short_message=receipt_text,
                esm_class=0x04,  # Delivery receipt flag
                data_coding=DataCoding.DEFAULT,
            )

            if success:
                logger.info(f'📧 Delivery receipt sent for message {message_id}')
            else:
                logger.warning(
                    f'⚠️  Failed to send delivery receipt for message {message_id}'
                )

        except Exception as e:
            logger.error(f'❌ Error sending delivery receipt: {e}')

    async def start(self) -> None:
        """Start the SMSC server."""
        await self.server.start()
        logger.info(f'🚀 SMSC server started on {self.server.host}:{self.server.port}')

    async def stop(self) -> None:
        """Stop the SMSC server with enhanced shutdown."""
        if self._shutdown_requested:
            return

        logger.info('🛑 SMSC server stopping - enhanced shutdown sequence will begin')
        self._shutdown_requested = True

        # Clean up all background tasks
        await self._cleanup_background_tasks()

        # Trigger the enhanced shutdown sequence via the server
        await self.server.stop()

    async def _cleanup_background_tasks(self) -> None:
        """Clean up all background tasks gracefully."""
        async with self._cleanup_lock:
            if not self._background_tasks:
                return

            logger.debug(f'Cancelling {len(self._background_tasks)} background tasks')

            for task in self._background_tasks.copy():
                if not task.done():
                    task.cancel()

            if self._background_tasks:
                await asyncio.gather(*self._background_tasks, return_exceptions=True)

            self._background_tasks.clear()

    async def broadcast_message(self, source_addr: str, message: str) -> None:
        """Broadcast message to all connected receiver clients."""
        bound_clients = self.server.get_bound_clients()
        receiver_clients = [
            client
            for client in bound_clients
            if client.bind_type in ('receiver', 'transceiver')
        ]

        if not receiver_clients:
            logger.info('📢 No receiver clients to broadcast to')
            return

        logger.info(f'📢 Broadcasting message to {len(receiver_clients)} clients')

        # Send to all clients concurrently
        tasks = []
        for client in receiver_clients:
            task = asyncio.create_task(
                self._send_broadcast_to_client(client, source_addr, message)
            )
            tasks.append(task)

        # Wait for all broadcasts to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Log results
        successful = sum(1 for result in results if result is True)
        failed = len(results) - successful

        logger.info(f'📢 Broadcast complete: {successful} successful, {failed} failed')

    async def _send_broadcast_to_client(
        self, client: ClientSession, source_addr: str, message: str
    ) -> bool:
        """Send broadcast message to a specific client."""
        try:
            success = await self.server.deliver_sm(
                target_system_id=client.system_id,
                source_addr=source_addr,
                destination_addr='BROADCAST',
                short_message=message,
                data_coding=DataCoding.DEFAULT,
            )

            if success:
                logger.debug(f'📤 Broadcast sent to {client.system_id}')
            else:
                logger.warning(f'⚠️  Failed to send broadcast to {client.system_id}')

            return success

        except Exception as e:
            logger.error(f'❌ Error sending broadcast to {client.system_id}: {e}')
            return False

    def get_server_stats(self) -> dict:
        """Get comprehensive server statistics."""
        bound_clients = self.server.get_bound_clients()
        shutdown_config = self.server.get_shutdown_config()

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
            'background_tasks': len(self._background_tasks),
            'shutdown_requested': self._shutdown_requested,
            'shutdown_config': shutdown_config,
        }

    async def _send_welcome_message(self, session: ClientSession) -> None:
        """Send welcome message to newly bound clients."""
        try:
            await asyncio.sleep(1)  # Brief delay after bind

            welcome_text = (
                f'Welcome to Enhanced SMSC, {session.system_id}! '
                'Enhanced shutdown features are active. '
                'Commands: ECHO <text>, HELP, STATUS, TIME, SHUTDOWN'
            )

            success = await self.server.deliver_sm(
                target_system_id=session.system_id,
                source_addr='SYSTEM',
                destination_addr=session.system_id,
                short_message=welcome_text,
                data_coding=DataCoding.DEFAULT,
            )

            if success:
                logger.info(f'📨 Welcome message sent to {session.system_id}')
            else:
                logger.warning(
                    f'⚠️  Failed to send welcome message to {session.system_id}'
                )

        except Exception as e:
            logger.error(
                f'❌ Error sending welcome message to {session.system_id}: {e}'
            )


async def main():
    """
    Main server function demonstrating enhanced shutdown capabilities.

    Features demonstrated:
    - Enhanced shutdown with client notifications
    - Graceful client disconnection handling
    - Background task management
    - Comprehensive logging and monitoring
    """
    # Create SMSC server with enhanced shutdown
    smsc = SMSCServer(host='localhost', port=2775)  # Changed to high port number

    # Background task references
    stats_task = None
    broadcast_task = None

    try:
        # Create and start background tasks
        stats_task = asyncio.create_task(run_stats_monitor(smsc))
        broadcast_task = asyncio.create_task(run_broadcast_scheduler(smsc))

        # Display startup information
        logger.info('🎯 Enhanced SMSC server ready for connections!')
        logger.info('🔧 Enhanced shutdown features:')
        config = smsc.server.get_shutdown_config()
        logger.info(f'   • Grace period: {config["grace_period"]}s')
        logger.info(f'   • Reminder delay: {config["reminder_delay"]}s')
        logger.info(f'   • Force disconnect timeout: {config["shutdown_timeout"]}s')
        logger.info('')
        logger.info('💡 Test enhanced shutdown by:')
        logger.info('   1. Connect clients (see examples/client.py)')
        logger.info('   2. Send "SHUTDOWN" command to trigger demo')
        logger.info('   3. Or press Ctrl+C to trigger signal-based shutdown')
        logger.info('   4. Watch the enhanced shutdown sequence in logs')
        logger.info('')

        # Run server until shutdown (serve_forever handles starting the server)
        await smsc.server.serve_forever()

    except Exception as e:
        logger.error(f'❌ Server error: {e}', exc_info=True)
    finally:
        # Clean up background tasks
        await cleanup_background_tasks(stats_task, broadcast_task)

        # Mark wrapper as stopped
        smsc._shutdown_requested = True
        logger.info('✅ SMSC server shutdown complete')


async def run_stats_monitor(smsc: SMSCServer) -> None:
    """Monitor and log server statistics periodically."""
    try:
        # Wait before first stats output
        await asyncio.sleep(30)

        while not smsc._shutdown_requested:
            stats = smsc.get_server_stats()
            logger.info(
                f'📊 Server Stats: {stats["total_connections"]} connections, '
                f'{stats["bound_clients"]} bound, {stats["total_messages"]} messages processed'
            )

            # Wait for next stats cycle
            await asyncio.sleep(60)  # Every minute

    except asyncio.CancelledError:
        logger.debug('📊 Stats monitor task cancelled')
        raise
    except Exception as e:
        logger.error(f'❌ Error in stats monitor: {e}')


async def run_broadcast_scheduler(smsc: SMSCServer) -> None:
    """Send periodic broadcast messages to demonstrate server capabilities."""
    try:
        # Wait before first broadcast
        await asyncio.sleep(120)  # Wait 2 minutes before first broadcast
        counter = 1

        while not smsc._shutdown_requested:
            await smsc.broadcast_message(
                source_addr='SYSTEM',
                message=f'📢 System broadcast #{counter} - Enhanced SMSC is running!',
            )
            counter += 1

            # Wait for next broadcast
            await asyncio.sleep(300)  # Every 5 minutes

    except asyncio.CancelledError:
        logger.debug('📢 Broadcast scheduler task cancelled')
        raise
    except Exception as e:
        logger.error(f'❌ Error in broadcast scheduler: {e}')


async def cleanup_background_tasks(*tasks) -> None:
    """Clean up background tasks gracefully."""
    for task in tasks:
        if task and not task.done():
            logger.debug(f'🧹 Cancelling background task: {task.get_name()}')
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            except Exception as e:
                logger.warning(f'⚠️  Error cancelling task {task.get_name()}: {e}')


async def simple_server_example():
    """
    Simple server example showcasing async context manager with enhanced shutdown.

    This demonstrates the cleanest way to use the enhanced shutdown features.
    """
    logger.info('🚀 Starting simple enhanced SMSC server...')

    async with SMPPServer(
        host='localhost',
        port=2775,  # Changed to high port number
        system_id='SIMPLE_SMSC',  # Fixed: SMPP system_id must be <= 16 characters
        setup_signal_handlers=True,
    ) as server:
        # Configure enhanced shutdown
        server.configure_shutdown(
            grace_period=10.0, reminder_delay=5.0, shutdown_timeout=15.0
        )

        logger.info('✅ Simple enhanced SMSC server running...')
        logger.info('🛑 Press Ctrl+C to see enhanced shutdown in action')

        # Server will run until shutdown signal (SIGTERM/SIGINT)
        # The async context manager will handle the enhanced shutdown automatically
        await server.serve_forever()


if __name__ == '__main__':
    print('🎯 Enhanced SMPP Server Example')
    print('=' * 40)
    print()
    print('Features demonstrated:')
    print('• Enhanced shutdown with client notifications')
    print('• Graceful client disconnection handling')
    print('• Interactive commands (ECHO, HELP, STATUS, TIME, SHUTDOWN)')
    print('• Background task management')
    print('• Comprehensive logging and monitoring')
    print()
    print('To test enhanced shutdown:')
    print('1. Run this server')
    print('2. Connect clients using examples/client.py')
    print("3. Send 'SHUTDOWN' command or press Ctrl+C")
    print('4. Watch the enhanced shutdown sequence in logs')
    print()
    print('Starting server...')
    print()

    # Run the main enhanced server
    asyncio.run(main())

    # Uncomment to run simple example instead:
    # print("Running simple server example...")
    # asyncio.run(simple_server_example())
