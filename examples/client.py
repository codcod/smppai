#!/usr/bin/env python3
"""
SMPP Client Example

This example demonstrates how to use the SMPP client to connect to an SMSC,
send SMS messages, and handle delivery receipts.

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

# Configure logging
logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SMSClient:
    """Example SMS client using SMPP"""

    def __init__(self, host: str, port: int, system_id: str, password: str):
        self.client = SMPPClient(
            host=host,
            port=port,
            system_id=system_id,
            password=password,
            system_type='SMS_CLIENT',
            enquire_link_interval=30.0,
            response_timeout=10.0,
        )

        # Set up event handlers
        self.client.on_deliver_sm = self.handle_deliver_sm
        self.client.on_connection_lost = self.handle_connection_lost
        self.client.on_bind_success = self.handle_bind_success
        self.client.on_unbind = self.handle_unbind

    def handle_deliver_sm(self, client: SMPPClient, pdu: DeliverSm) -> None:
        """Handle incoming deliver_sm (delivery receipts or MO SMS)"""
        try:
            message = pdu.short_message.decode('utf-8', errors='ignore')

            # Check if this is a delivery receipt
            if pdu.esm_class & 0x04:  # Delivery receipt
                logger.info('Delivery receipt received:')
                logger.info(f'  From: {pdu.source_addr}')
                logger.info(f'  To: {pdu.destination_addr}')
                logger.info(f'  Receipt: {message}')
            else:  # Mobile Originated SMS
                logger.info('MO SMS received:')
                logger.info(f'  From: {pdu.source_addr}')
                logger.info(f'  To: {pdu.destination_addr}')
                logger.info(f'  Message: {message}')

        except Exception as e:
            logger.error(f'Error handling deliver_sm: {e}')

    def handle_connection_lost(self, client: SMPPClient, error: Exception) -> None:
        """Handle connection lost event"""
        logger.error(f'Connection lost: {error}')
        # Could implement reconnection logic here

    def handle_bind_success(self, client: SMPPClient, bind_type: BindType) -> None:
        """Handle successful bind"""
        logger.info(f'Successfully bound as {bind_type.value}')

    def handle_unbind(self, client: SMPPClient) -> None:
        """Handle unbind event"""
        logger.info('Client unbound from SMSC')

    async def connect_and_bind(
        self, bind_type: BindType = BindType.TRANSCEIVER
    ) -> None:
        """Connect to SMSC and bind"""
        try:
            # Connect to SMSC
            await self.client.connect()
            logger.info('Connected to SMSC')

            # Bind as transceiver (can send and receive)
            if bind_type == BindType.TRANSMITTER:
                await self.client.bind_transmitter()
            elif bind_type == BindType.RECEIVER:
                await self.client.bind_receiver()
            else:
                await self.client.bind_transceiver()

        except Exception as e:
            logger.error(f'Failed to connect and bind: {e}')
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

            logger.info(f'SMS sent successfully, message ID: {message_id}')
            return message_id

        except Exception as e:
            logger.error(f'Failed to send SMS: {e}')
            return None

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

            logger.info(f'Unicode SMS sent successfully, message ID: {message_id}')
            return message_id

        except Exception as e:
            logger.error(f'Failed to send Unicode SMS: {e}')
            return None

    async def disconnect(self) -> None:
        """Disconnect from SMSC"""
        try:
            await self.client.disconnect()
            logger.info('Disconnected from SMSC')
        except Exception as e:
            logger.error(f'Error during disconnect: {e}')


async def main():
    """Main example function"""
    # SMSC connection details
    SMSC_HOST = 'localhost'
    SMSC_PORT = 2775
    SYSTEM_ID = 'test_client'
    PASSWORD = 'password'

    # Create SMS client
    sms_client = SMSClient(SMSC_HOST, SMSC_PORT, SYSTEM_ID, PASSWORD)

    try:
        # Connect and bind as transceiver
        await sms_client.connect_and_bind(BindType.TRANSCEIVER)

        # Send a simple SMS
        await sms_client.send_sms(
            source_addr='1234',
            destination_addr='5678',
            message='Hello from SMPP client!',
            request_delivery_receipt=True,
        )

        # Send a Unicode SMS
        await sms_client.send_unicode_sms(
            source_addr='1234',
            destination_addr='5678',
            message='Hello 世界! 🌍',
            request_delivery_receipt=True,
        )

        # Keep the connection alive for a while to receive delivery receipts
        logger.info('Waiting for delivery receipts...')
        await asyncio.sleep(10)

        # Send multiple messages
        for i in range(3):
            await sms_client.send_sms(
                source_addr='1234',
                destination_addr='5678',
                message=f'Test message {i + 1}',
                request_delivery_receipt=True,
            )
            await asyncio.sleep(1)

        # Wait a bit more
        await asyncio.sleep(5)

    except KeyboardInterrupt:
        logger.info('Interrupted by user')
    except Exception as e:
        logger.error(f'Error in main: {e}')
    finally:
        # Clean disconnect
        await sms_client.disconnect()


async def simple_send_example():
    """Simple example of sending one SMS"""
    async with SMPPClient(
        host='localhost', port=2775, system_id='test_client', password='password'
    ) as client:
        # Bind as transmitter
        await client.bind_transmitter()

        # Send SMS
        message_id = await client.submit_sm(
            source_addr='1234', destination_addr='5678', short_message='Hello World!'
        )

        print(f'Message sent with ID: {message_id}')


async def monitor_messages_example():
    """Example of monitoring incoming messages"""
    client = SMPPClient(
        host='localhost', port=2775, system_id='test_receiver', password='password'
    )

    def handle_message(client: SMPPClient, pdu: DeliverSm):
        message = pdu.short_message.decode('utf-8', errors='ignore')
        print(f'Received message from {pdu.source_addr}: {message}')

    client.on_deliver_sm = handle_message

    try:
        await client.connect()
        await client.bind_receiver()

        print('Monitoring for incoming messages... Press Ctrl+C to stop')

        # Keep running until interrupted
        while True:
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        print('\nStopping...')
    finally:
        await client.disconnect()


if __name__ == '__main__':
    # Run the main example
    asyncio.run(main())

    # Uncomment to run other examples:
    # asyncio.run(simple_send_example())
    # asyncio.run(monitor_messages_example())
