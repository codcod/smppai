#!/usr/bin/env python3
"""
SMPP Client Example

This example demonstrates how to use the SMPP client to connect to an SMSC,
send SMS messages, handle delivery receipts, and properly handle enhanced shutdown
notifications from the server.

Enhanced Shutdown Features:
- Receives and responds to server shutdown notifications
- Graceful disconnection when server requests shutdown
- Proper handling of connection loss during shutdown
- Interactive commands for testing shutdown scenarios

Updated for the new modular code structure with clean imports from the main smpp package.
"""

import asyncio
import logging
import os
import sys
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from smpp import (
    BindType,
    DataCoding,
    DeliverSm,
    NpiType,
    RegisteredDelivery,
    SMPPClient,
    TonType,
)

# Configure logging with enhanced format for shutdown monitoring
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)-8s] [%(name)s] %(message)s',
    datefmt='%H:%M:%S',
)
logger = logging.getLogger(__name__)


class SMSClient:
    """
    Example SMS client using SMPP with enhanced shutdown handling.

    Features:
    - Enhanced shutdown notification handling
    - Graceful disconnection on server shutdown
    - Interactive command support
    - Proper connection lifecycle management
    """

    def __init__(self, host: str, port: int, system_id: str, password: str):
        self.client = SMPPClient(
            host=host,
            port=port,
            system_id=system_id,
            password=password,
            system_type='CLIENT',  # Fixed: SMPP system_type must be <= 13 characters
            enquire_link_interval=30.0,
            response_timeout=10.0,
        )

        # Enhanced shutdown handling with thread safety
        self._shutdown_lock = asyncio.Lock()
        self._shutdown_state = 'running'  # running, shutting_down, stopped
        self._shutdown_grace_period = 0
        self._received_shutdown_notification = False
        self._received_shutdown_reminder = False

        # Set up event handlers
        self.client.on_deliver_sm = self.handle_deliver_sm
        self.client.on_connection_lost = self.handle_connection_lost
        self.client.on_bind_success = self.handle_bind_success
        self.client.on_unbind = self.handle_unbind

    def handle_deliver_sm(self, client: SMPPClient, pdu: DeliverSm) -> None:
        """Handle incoming deliver_sm with enhanced shutdown notification detection."""
        try:
            message = pdu.short_message.decode('utf-8', errors='ignore')

            # Check if this is a delivery receipt
            if pdu.esm_class & 0x04:  # Delivery receipt
                logger.info('📧 Delivery receipt received:')
                logger.info(f'   From: {pdu.source_addr} → To: {pdu.destination_addr}')
                logger.info(f'   Receipt: {message}')

            # Check for shutdown notifications from the server
            elif self._is_shutdown_notification(pdu, message):
                self._handle_shutdown_notification(pdu, message)

            else:  # Mobile Originated SMS or server message
                logger.info('📥 Message received:')
                logger.info(f'   From: {pdu.source_addr} → To: {pdu.destination_addr}')
                logger.info(f'   Content: "{message}"')

                # Handle interactive responses if this is a response to our commands
                if pdu.source_addr == 'SYSTEM':
                    logger.info('🤖 Server response received')

        except Exception as e:
            logger.error(f'❌ Error handling deliver_sm: {e}')

    def _is_shutdown_notification(self, pdu: DeliverSm, message: str) -> bool:
        """Check if this message is a server shutdown notification."""
        # Check for shutdown notification patterns
        shutdown_indicators = [
            'shutdown notification',
            'shutdown reminder',
            'server shutdown',
            'server shutting down',
            'final warning',
            'grace period',
        ]

        message_lower = message.lower()
        is_from_system = pdu.source_addr in (
            'SYSTEM',
            'SMSC',
            'DEMO_SMSC',
        )  # Fixed: Updated for SMPP-compliant system IDs

        return is_from_system and any(
            indicator in message_lower for indicator in shutdown_indicators
        )

    def _handle_shutdown_notification(self, pdu: DeliverSm, message: str) -> None:
        """Handle server shutdown notifications with appropriate responses."""
        message_lower = message.lower()

        if 'reminder' in message_lower or 'final warning' in message_lower:
            if not self._received_shutdown_reminder:
                logger.warning('🔔 SHUTDOWN REMINDER received from server!')
                logger.warning(f'   Message: "{message}"')
                logger.warning(
                    '⚠️  Server will force disconnect soon - preparing for graceful shutdown'
                )
                self._received_shutdown_reminder = True
                # Start graceful shutdown process
                asyncio.create_task(self._initiate_graceful_shutdown(urgent=True))

        elif not self._received_shutdown_notification:
            logger.info('🛑 SHUTDOWN NOTIFICATION received from server!')
            logger.info(f'   Message: "{message}"')

            # Extract grace period if mentioned
            try:
                if 'grace period:' in message_lower:
                    # Try to extract the grace period value
                    parts = message.split('Grace period:')
                    if len(parts) > 1:
                        grace_str = parts[1].split('s')[0].strip()
                        self._shutdown_grace_period = float(grace_str)
                        logger.info(
                            f'📅 Grace period: {self._shutdown_grace_period} seconds'
                        )
            except Exception:
                pass  # Continue even if grace period extraction fails

            self._received_shutdown_notification = True
            logger.info(
                '✅ Acknowledged shutdown notification - will disconnect gracefully'
            )

            # Start graceful shutdown process
            asyncio.create_task(self._initiate_graceful_shutdown())

    async def _initiate_graceful_shutdown(self, urgent: bool = False) -> None:
        """Thread-safe graceful shutdown process."""
        async with self._shutdown_lock:
            if self._shutdown_state != 'running':
                return  # Already shutting down or stopped

            self._shutdown_state = 'shutting_down'

        try:
            if urgent:
                logger.warning('🚨 Urgent shutdown - disconnecting immediately')
                delay = 0.1  # Minimal delay for urgent shutdown
            else:
                # Give some time for any pending operations, but respect server's grace period
                if self._shutdown_grace_period > 0:
                    # Use a fraction of the server's grace period, but cap it reasonably
                    delay = min(max(0.1, self._shutdown_grace_period * 0.5), 2.0)
                else:
                    delay = 0.5  # Default to 0.5s instead of 3.0s for faster tests
                logger.info(f'⏱️  Graceful shutdown in {delay:.1f} seconds...')

            await asyncio.sleep(delay)

            logger.info('👋 Initiating graceful disconnect from server')
            await self.disconnect()

        except asyncio.CancelledError:
            raise  # Re-raise cancellation
        except Exception as e:
            logger.error(f'❌ Error during graceful shutdown: {e}')
        finally:
            async with self._shutdown_lock:
                self._shutdown_state = 'stopped'

    def handle_connection_lost(self, client: SMPPClient, error: Exception) -> None:
        """Handle connection lost event with enhanced shutdown awareness."""
        if self._shutdown_state != 'running' or self._received_shutdown_notification:
            logger.info('🔌 Connection closed - server shutdown completed')
        else:
            logger.error(f'❌ Unexpected connection lost: {error}')
            logger.warning(
                '🛑 Server has disconnected unexpectedly - initiating graceful client shutdown'
            )
            # When server disconnects unexpectedly, treat it as a shutdown request
            asyncio.create_task(self._initiate_graceful_shutdown(urgent=True))

    def handle_bind_success(self, client: SMPPClient, bind_type: BindType) -> None:
        """Handle successful bind with enhanced logging."""
        logger.info(f'🔐 Successfully bound as {bind_type.value}')
        logger.info('✅ Client ready to send/receive messages')
        logger.info('🛑 Will respond appropriately to server shutdown notifications')

    def handle_unbind(self, client: SMPPClient) -> None:
        """Handle unbind event with enhanced logging."""
        if self._shutdown_state == 'shutting_down':
            logger.info('👋 Gracefully unbound from SMSC during shutdown')
        else:
            logger.info('🔓 Client unbound from SMSC')

    async def connect_and_bind(
        self, bind_type: BindType = BindType.TRANSCEIVER
    ) -> None:
        """Connect to SMSC and bind with enhanced shutdown awareness."""
        try:
            # Connect to SMSC
            await self.client.connect()
            logger.info('🔗 Connected to SMSC')

            # Bind as requested type
            if bind_type == BindType.TRANSMITTER:
                await self.client.bind_transmitter()
            elif bind_type == BindType.RECEIVER:
                await self.client.bind_receiver()
            else:
                await self.client.bind_transceiver()

        except Exception as e:
            logger.error(f'❌ Failed to connect and bind: {e}')
            raise

    async def send_sms(
        self,
        source_addr: str,
        destination_addr: str,
        message: str,
        request_delivery_receipt: bool = False,
        source_ton: int = TonType.INTERNATIONAL,
        source_npi: int = NpiType.ISDN,
        dest_ton: int = TonType.INTERNATIONAL,
        dest_npi: int = NpiType.ISDN,
    ) -> Optional[str]:
        """Send SMS message"""
        try:
            if not self.client.is_bound:
                if self.shutdown_requested:
                    logger.debug('🔇 Skipping SMS send - shutdown in progress')
                    return None
                raise Exception('Client is not bound to SMSC')

            # Set registered delivery if receipt is requested
            registered_delivery = (
                RegisteredDelivery.SUCCESS_FAILURE
                if request_delivery_receipt
                else RegisteredDelivery.NO_RECEIPT
            )

            message_id = await self.client.submit_sm(
                source_addr=source_addr,
                destination_addr=destination_addr,
                short_message=message,
                source_addr_ton=source_ton,
                source_addr_npi=source_npi,
                dest_addr_ton=dest_ton,
                dest_addr_npi=dest_npi,
                registered_delivery=registered_delivery,
                data_coding=DataCoding.DEFAULT,
            )

            logger.info(f'📤 SMS sent successfully, message ID: {message_id}')
            return message_id

        except Exception as e:
            if not self.shutdown_requested:
                logger.error(f'❌ Failed to send SMS: {e}')
            return None

    async def send_command(self, command: str) -> Optional[str]:
        """
        Send a command to the server (for testing enhanced shutdown).

        Uses proper SMPP address types to ensure validation passes:
        - Source: Numeric short code with UNKNOWN TON/NPI
        - Destination: Alphanumeric "SERVER" with ALPHANUMERIC TON
        """
        return await self.send_sms(
            source_addr='99999',  # Use numeric address for source
            destination_addr='SERVER',  # Use alphanumeric destination for server commands
            message=command,
            request_delivery_receipt=False,
            source_ton=TonType.UNKNOWN,  # Unknown for numeric short code
            source_npi=NpiType.UNKNOWN,
            dest_ton=TonType.ALPHANUMERIC,  # Alphanumeric for "SERVER" destination
            dest_npi=NpiType.UNKNOWN,
        )

    async def send_unicode_sms(
        self,
        source_addr: str,
        destination_addr: str,
        message: str,
        request_delivery_receipt: bool = False,
    ) -> Optional[str]:
        """Send Unicode SMS message"""
        try:
            if not self.client.is_bound:
                raise Exception('Client is not bound to SMSC')

            # Set registered delivery if receipt is requested
            registered_delivery = (
                RegisteredDelivery.SUCCESS_FAILURE
                if request_delivery_receipt
                else RegisteredDelivery.NO_RECEIPT
            )

            # Send using the high-level API with UCS2 encoding
            message_id = await self.client.submit_sm(
                source_addr=source_addr,
                destination_addr=destination_addr,
                short_message=message,
                source_addr_ton=TonType.INTERNATIONAL,
                source_addr_npi=NpiType.ISDN,
                dest_addr_ton=TonType.INTERNATIONAL,
                dest_addr_npi=NpiType.ISDN,
                data_coding=DataCoding.UCS2,
                registered_delivery=registered_delivery,
            )

            logger.info(f'📤 Unicode SMS sent successfully, message ID: {message_id}')
            return message_id

        except Exception as e:
            logger.error(f'❌ Failed to send Unicode SMS: {e}')
            return None

    async def disconnect(self) -> None:
        """Disconnect from SMSC with enhanced shutdown handling."""
        try:
            if self.client.is_connected:
                await self.client.disconnect()
                logger.info('👋 Disconnected from SMSC')
            else:
                logger.info('🔌 Already disconnected from SMSC')
        except Exception as e:
            logger.error(f'❌ Error during disconnect: {e}')

    @property
    def shutdown_requested(self) -> bool:
        """Check if shutdown has been requested."""
        return self._shutdown_state != 'running'

    def get_shutdown_status(self) -> dict:
        """Get current shutdown status information."""
        return {
            'shutdown_requested': self.shutdown_requested,
            'shutdown_state': self._shutdown_state,
            'received_notification': self._received_shutdown_notification,
            'received_reminder': self._received_shutdown_reminder,
            'grace_period': self._shutdown_grace_period,
            'is_connected': self.client.is_connected,
            'is_bound': self.client.is_bound,
        }


async def main():
    """
    Main example function demonstrating enhanced shutdown handling.

    Features demonstrated:
    - Connecting and binding to SMSC
    - Sending various types of messages
    - Interactive command support
    - Enhanced shutdown notification handling
    - Graceful disconnection
    """
    # SMSC connection details - compatible with SMPP protocol (max 8 chars for password)
    SMSC_HOST = 'localhost'
    SMSC_PORT = 9999  # Changed to high port number
    SYSTEM_ID = 'test_client'
    PASSWORD = 'password'  # Fixed: SMPP passwords must be <= 8 characters

    # Create enhanced SMS client
    sms_client = SMSClient(SMSC_HOST, SMSC_PORT, SYSTEM_ID, PASSWORD)

    try:
        logger.info('🚀 Enhanced SMPP Client starting...')
        logger.info(
            '🔧 Features: Shutdown notification handling, graceful disconnection'
        )
        logger.info('')

        # Connect and bind as transceiver (can send and receive)
        await sms_client.connect_and_bind(BindType.TRANSCEIVER)

        # Send initial greeting
        await sms_client.send_sms(
            source_addr='12345',
            destination_addr='67890',
            message='Hello from enhanced SMPP client!',
            request_delivery_receipt=True,
        )

        # Test server commands
        logger.info('🧪 Testing server commands...')

        # Send HELP command to see available server commands
        await sms_client.send_command('HELP')
        await asyncio.sleep(2)

        # Send STATUS command to see server status
        await sms_client.send_command('STATUS')
        await asyncio.sleep(2)

        # Send CLIENTS command to see connected clients
        await sms_client.send_command('CLIENTS')
        await asyncio.sleep(2)

        # Send a Unicode message
        await sms_client.send_unicode_sms(
            source_addr='12345',
            destination_addr='67890',
            message='Unicode test: Hello 世界! 🌍 Enhanced shutdown ready!',
            request_delivery_receipt=True,
        )

        # Simulate some activity while monitoring for shutdown notifications
        logger.info('📡 Monitoring for messages and shutdown notifications...')
        logger.info('💡 To test enhanced shutdown:')
        logger.info('   1. Send "SHUTDOWN" command: triggers demo shutdown')
        logger.info('   2. Press Ctrl+C on server: triggers signal-based shutdown')
        logger.info('   3. Watch this client respond to shutdown notifications')
        logger.info('')

        # Keep the client active and responsive
        activity_counter = 0
        while not sms_client.shutdown_requested:
            # Check if we're still connected before trying to send messages
            if not sms_client.client.is_connected:
                logger.warning('⚠️  No longer connected to server - stopping activity')
                break

            # Send periodic activity messages
            if activity_counter % 30 == 0:  # Every 30 seconds
                try:
                    await sms_client.send_sms(
                        source_addr='12345',
                        destination_addr='67890',
                        message=f'Periodic activity message #{activity_counter // 30 + 1}',
                        request_delivery_receipt=True,
                    )
                    logger.info(
                        f'📊 Activity counter: {activity_counter} (client running normally)'
                    )
                except Exception as e:
                    logger.warning(f'⚠️  Failed to send activity message: {e}')
                    # If we can't send messages, something is wrong
                    break

            # Check if user wants to trigger shutdown demo
            if activity_counter == 60:  # After 1 minute, offer to test shutdown
                logger.info('')
                logger.info(
                    '🧪 Testing enhanced shutdown - sending SHUTDOWN command...'
                )
                try:
                    await sms_client.send_command('SHUTDOWN')
                    logger.info(
                        '🎬 Enhanced shutdown demo initiated! Watch the logs...'
                    )
                except Exception as e:
                    logger.warning(f'⚠️  Failed to send shutdown command: {e}')

            await asyncio.sleep(2)
            activity_counter += 2

            # Break if we've been running for too long without shutdown
            if activity_counter > 300:  # 5 minutes max
                logger.info('⏰ Timeout reached - ending demo')
                break

        # If shutdown was requested, wait a bit for it to complete
        if sms_client.shutdown_requested:
            logger.info('⏳ Waiting for shutdown to complete...')
            await asyncio.sleep(3)

    except KeyboardInterrupt:
        logger.info('🔴 Client interrupted by user')
    except Exception as e:
        logger.error(f'❌ Error in main: {e}', exc_info=True)
    finally:
        # Show final shutdown status
        status = sms_client.get_shutdown_status()
        logger.info('📋 Final shutdown status:')
        for key, value in status.items():
            logger.info(f'   {key}: {value}')

        # Clean disconnect
        await sms_client.disconnect()
        logger.info('✅ Enhanced SMPP client shutdown complete')


async def simple_send_example():
    """Simple example of sending one SMS with enhanced shutdown awareness."""
    logger.info('🚀 Simple enhanced client example...')

    async with SMPPClient(
        host='localhost',
        port=9999,  # Changed to high port number
        system_id='test_client',
        password='password',  # Fixed: SMPP passwords must be <= 8 characters
    ) as client:
        # Bind as transmitter
        await client.bind_transmitter()
        logger.info('🔐 Bound as transmitter')

        # Send SMS
        message_id = await client.submit_sm(
            source_addr='12345',
            destination_addr='67890',
            short_message='Hello World from enhanced client!',
        )

        logger.info(f'📤 Message sent with ID: {message_id}')


async def monitor_messages_example():
    """
    Example of monitoring incoming messages with enhanced shutdown handling.

    This client will properly handle server shutdown notifications.
    """
    logger.info('🎧 Enhanced message monitoring client starting...')

    client = SMPPClient(
        host='localhost',
        port=9999,  # Changed to high port number
        system_id='test_receiver',
        password='password',  # Fixed: SMPP passwords must be <= 8 characters
    )

    shutdown_requested = False

    def handle_message(client: SMPPClient, pdu: DeliverSm):
        nonlocal shutdown_requested

        message = pdu.short_message.decode('utf-8', errors='ignore')

        # Check for shutdown notifications
        if (
            pdu.source_addr
            in ('SYSTEM', 'SMSC')  # Fixed: Updated for SMPP-compliant system IDs
            and 'shutdown' in message.lower()
        ):
            logger.warning(f'🛑 Server shutdown notification: {message}')
            logger.info('✅ Will disconnect gracefully...')
            shutdown_requested = True
        else:
            logger.info(f'📥 Message from {pdu.source_addr}: {message}')

    client.on_deliver_sm = handle_message

    try:
        await client.connect()
        await client.bind_receiver()
        logger.info('🔐 Bound as receiver')

        logger.info('👂 Monitoring for incoming messages and shutdown notifications...')
        logger.info('🛑 Press Ctrl+C to stop, or server will notify when shutting down')

        # Keep running until interrupted or shutdown requested
        while not shutdown_requested:
            await asyncio.sleep(1)

        logger.info('🏁 Shutdown requested - exiting gracefully')

    except KeyboardInterrupt:
        logger.info('🔴 Client interrupted by user')
    finally:
        await client.disconnect()
        logger.info('👋 Monitor client disconnected')


async def interactive_client_example():
    """
    Interactive client that can send commands to test enhanced shutdown.
    """
    logger.info('🎮 Interactive enhanced SMPP client starting...')

    # Create enhanced client
    sms_client = SMSClient(
        'localhost', 9999, 'demo_client', 'demo_pas'
    )  # Changed to high port number

    try:
        await sms_client.connect_and_bind(BindType.TRANSCEIVER)

        logger.info('')
        logger.info('🎯 Interactive commands available:')
        logger.info('   HELP     - Show server help')
        logger.info('   STATUS   - Show server status')
        logger.info('   CLIENTS  - List connected clients')
        logger.info('   TIME     - Get server time')
        logger.info('   SHUTDOWN - Trigger enhanced shutdown demo')
        logger.info('   QUIT     - Disconnect client')
        logger.info('')
        logger.info('💡 The client will automatically handle shutdown notifications!')
        logger.info('')

        # Send initial status request
        await sms_client.send_command('STATUS')

        # Interactive loop
        command_count = 0
        while not sms_client.shutdown_requested and command_count < 10:
            # Simulate interactive commands
            commands = ['HELP', 'STATUS', 'CLIENTS', 'TIME']
            command = commands[command_count % len(commands)]

            logger.info(f'📤 Sending command: {command}')
            await sms_client.send_command(command)

            # After a few commands, trigger shutdown demo
            if command_count == 3:
                logger.info('')
                logger.info('🧪 Testing enhanced shutdown...')
                await sms_client.send_command('SHUTDOWN')
                logger.info('🎬 Shutdown demo initiated!')

            await asyncio.sleep(5)
            command_count += 1

        # Wait for shutdown to complete if requested
        if sms_client.shutdown_requested:
            logger.info('⏳ Waiting for shutdown sequence to complete...')
            await asyncio.sleep(5)

    except Exception as e:
        logger.error(f'❌ Interactive client error: {e}')
    finally:
        await sms_client.disconnect()
        logger.info('✅ Interactive client session ended')


if __name__ == '__main__':
    print('🎯 Enhanced SMPP Client Example')
    print('=' * 40)
    print()
    print('Features demonstrated:')
    print('• Enhanced shutdown notification handling')
    print('• Graceful disconnection on server shutdown')
    print('• Interactive command support')
    print('• Proper connection lifecycle management')
    print('• Automatic response to server shutdown notifications')
    print()
    print('To test enhanced shutdown:')
    print('1. Start the enhanced server (examples/server.py)')
    print('2. Run this client')
    print('3. Watch how client handles server shutdown notifications')
    print('4. Client will disconnect gracefully when server shuts down')
    print()
    print('Starting enhanced client...')
    print()

    # Run the main enhanced client example
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('\n🛑 Client interrupted - enhanced shutdown handling demonstrated')

    # Uncomment to run other examples:
    # print("Running simple send example...")
    # asyncio.run(simple_send_example())
    #
    # print("Running message monitor example...")
    # asyncio.run(monitor_messages_example())
    #
    # print("Running interactive client example...")
    # asyncio.run(interactive_client_example())
