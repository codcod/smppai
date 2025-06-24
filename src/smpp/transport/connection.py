"""
SMPP Connection Handling

This module provides async TCP connection handling for SMPP protocol,
including connection management, PDU sending/receiving, and connection state tracking.
"""

import asyncio
import logging
import struct
import time
from enum import Enum
from typing import Callable, Dict, Optional, Tuple

from smpp.exceptions import (
    SMPPConnectionException,
    SMPPPDUException,
    SMPPTimeoutException,
    SMPPValidationException,
)
from smpp.protocol.constants import PDU_HEADER_SIZE
from smpp.protocol.pdu import PDU, decode_pdu
from smpp.protocol.pdu.session import EnquireLink
from smpp.protocol.validation import validate_pdu_structure

logger = logging.getLogger(__name__)


class ConnectionState(Enum):
    """SMPP Connection States"""

    CLOSED = 'CLOSED'
    OPEN = 'OPEN'
    BOUND_TX = 'BOUND_TX'
    BOUND_RX = 'BOUND_RX'
    BOUND_TRX = 'BOUND_TRX'


class SMPPConnection:
    """
    Async SMPP Connection Handler

    Manages TCP connection, PDU encoding/decoding, and connection state.
    Provides async methods for sending and receiving SMPP PDUs.
    """

    def __init__(
        self,
        host: str,
        port: int,
        reader: Optional[asyncio.StreamReader] = None,
        writer: Optional[asyncio.StreamWriter] = None,
        read_timeout: float = 30.0,
        write_timeout: float = 30.0,
        enquire_link_interval: float = 30.0,
    ):
        """
        Initialize SMPP connection

        Args:
            host: Remote host address
            port: Remote port number
            reader: Optional existing StreamReader (for server connections)
            writer: Optional existing StreamWriter (for server connections)
            read_timeout: Timeout for read operations in seconds
            write_timeout: Timeout for write operations in seconds
            enquire_link_interval: Interval for enquire_link keepalive in seconds
        """
        self.host = host
        self.port = port
        self.read_timeout = read_timeout
        self.write_timeout = write_timeout
        self.enquire_link_interval = enquire_link_interval

        self._reader = reader
        self._writer = writer
        self._state = ConnectionState.CLOSED
        self._connected = False
        self._sequence_counter = 1  # Start at 1
        self._pending_pdus: Dict[int, Tuple[asyncio.Future[PDU], float]] = {}
        self.max_pending_pdus = 1000  # Default limit for pending PDUs
        self.cleanup_interval = 60  # Default cleanup interval in seconds
        self._receive_task: Optional[asyncio.Task] = None
        self._enquire_link_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None
        self._last_activity = time.time()

        # Event handlers
        self.on_pdu_received: Optional[Callable[[PDU], None]] = None
        self.on_connection_lost: Optional[Callable[[Exception], None]] = None
        self.on_state_changed: Optional[
            Callable[[ConnectionState, ConnectionState], None]
        ] = None

    @property
    def state(self) -> ConnectionState:
        """Get current connection state"""
        return self._state

    @property
    def is_connected(self) -> bool:
        """Check if connection is established"""
        return self._connected and self._writer is not None

    @property
    def is_bound(self) -> bool:
        """Check if connection is bound"""
        return self._state in (
            ConnectionState.BOUND_TX,
            ConnectionState.BOUND_RX,
            ConnectionState.BOUND_TRX,
        )

    def _set_state(self, new_state: ConnectionState) -> None:
        """Set connection state and trigger state change event"""
        old_state = self._state
        if old_state != new_state:
            self._state = new_state
            logger.debug(
                f'Connection state changed: {old_state.value} -> {new_state.value}'
            )
            if self.on_state_changed:
                try:
                    self.on_state_changed(old_state, new_state)
                except Exception as e:
                    logger.exception(f'Error in state change handler: {e}')

    def _get_next_sequence(self) -> int:
        """Get next sequence number"""
        current = self._sequence_counter
        self._sequence_counter += 1
        if self._sequence_counter > 0x7FFFFFFF:
            self._sequence_counter = 1
        return current

    async def connect(self) -> None:
        """Establish TCP connection"""
        if self.is_connected:
            raise SMPPConnectionException('Already connected')

        try:
            logger.info(f'Connecting to {self.host}:{self.port}')
            self._reader, self._writer = await asyncio.wait_for(
                asyncio.open_connection(self.host, self.port),
                timeout=self.write_timeout,
            )

            self._connected = True
            self._set_state(ConnectionState.OPEN)
            self._last_activity = time.time()

            # Start background tasks
            self._receive_task = asyncio.create_task(self._receive_loop())
            self._enquire_link_task = asyncio.create_task(self._enquire_link_loop())
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())

            logger.info(f'Connected to {self.host}:{self.port}')

        except asyncio.TimeoutError:
            raise SMPPTimeoutException(f'Connection timeout to {self.host}:{self.port}')
        except Exception as e:
            raise SMPPConnectionException(
                f'Failed to connect to {self.host}:{self.port}: {e}'
            )

    async def disconnect(self) -> None:
        """Close TCP connection"""
        if not self.is_connected:
            return

        logger.info('Disconnecting...')

        # Collect and cancel background tasks
        tasks_to_cancel = []
        if self._receive_task and not self._receive_task.done():
            tasks_to_cancel.append(self._receive_task)
        if self._enquire_link_task and not self._enquire_link_task.done():
            tasks_to_cancel.append(self._enquire_link_task)
        if self._cleanup_task and not self._cleanup_task.done():
            tasks_to_cancel.append(self._cleanup_task)

        # Clear task references immediately to prevent re-entry
        self._receive_task = None
        self._enquire_link_task = None
        self._cleanup_task = None

        # Cancel all tasks and wait for them to complete
        for task in tasks_to_cancel:
            task.cancel()

        # Wait for all tasks to complete cancellation
        if tasks_to_cancel:
            try:
                await asyncio.gather(*tasks_to_cancel, return_exceptions=True)
            except Exception as e:
                logger.debug(f'Error during task cancellation: {e}')

        # Close writer
        if self._writer:
            try:
                self._writer.close()
                await self._writer.wait_closed()
            except Exception as e:
                logger.warning(f'Error closing writer: {e}')
            finally:
                self._writer = None

        self._reader = None
        self._connected = False
        self._set_state(ConnectionState.CLOSED)

        # Complete pending PDUs with error
        futures_to_cleanup = []
        for future, _ in self._pending_pdus.values():
            if not future.done():
                future.set_exception(SMPPConnectionException('Connection closed'))
                futures_to_cleanup.append(future)
        self._pending_pdus.clear()

        # Clean up futures to prevent warnings
        for future in futures_to_cleanup:
            try:
                future.exception()
            except Exception:
                pass

        logger.info('Disconnected')

    async def send_pdu(
        self, pdu: PDU, wait_response: bool = True, timeout: Optional[float] = None
    ) -> Optional[PDU]:
        """
        Send PDU and optionally wait for response

        Args:
            pdu: PDU to send
            wait_response: Whether to wait for response PDU
            timeout: Timeout for response (uses write_timeout if None)

        Returns:
            Response PDU if wait_response=True, None otherwise
        """
        if not self.is_connected:
            raise SMPPConnectionException('Not connected')

        if pdu.sequence_number == 0:
            pdu.sequence_number = self._get_next_sequence()

        # Prepare future for response if needed
        response_future: Optional[asyncio.Future[PDU]] = None
        if wait_response:
            response_future = asyncio.Future[PDU]()
            self._pending_pdus[pdu.sequence_number] = (response_future, time.time())

        try:
            # Encode and send PDU
            data = pdu.encode()
            logger.debug(
                f'Sending PDU: {pdu.__class__.__name__} (seq={pdu.sequence_number}, len={len(data)})'
            )

            await asyncio.wait_for(
                self._send_data(data), timeout=timeout or self.write_timeout
            )

            self._last_activity = time.time()

            # Wait for response if requested
            if wait_response and response_future:
                try:
                    response = await asyncio.wait_for(
                        response_future, timeout=timeout or self.read_timeout
                    )
                    return response
                except asyncio.TimeoutError:
                    raise SMPPTimeoutException(
                        f'Response timeout for PDU {pdu.__class__.__name__}'
                    )
                finally:
                    self._pending_pdus.pop(pdu.sequence_number, None)

        except Exception as e:
            if wait_response:
                self._pending_pdus.pop(pdu.sequence_number, None)
            if isinstance(e, (SMPPConnectionException, SMPPTimeoutException)):
                raise
            elif isinstance(e, asyncio.TimeoutError):
                raise SMPPTimeoutException(
                    f'Response timeout for PDU {pdu.__class__.__name__}'
                )
            raise SMPPConnectionException(f'Failed to send PDU: {e}')

        return None

    async def _send_data(self, data: bytes) -> None:
        """Send raw data over connection"""
        if not self._writer:
            raise SMPPConnectionException('Writer not available')

        try:
            self._writer.write(data)
            await self._writer.drain()
        except Exception as e:
            # Handle connection error but don't raise from within the async context
            # to avoid coroutine cleanup issues in tests
            try:
                await self._handle_connection_error(e)
            except Exception:
                # Ignore errors in error handler to prevent cascading issues
                pass
            raise SMPPConnectionException(f'Failed to send PDU: {e}')

    async def _receive_loop(self) -> None:
        """Background task to receive and process PDUs"""
        logger.debug('Starting receive loop')

        try:
            while self.is_connected:
                try:
                    pdu = await self._receive_pdu()
                    if pdu:
                        await self._handle_received_pdu(pdu)
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f'Error in receive loop: {e}')
                    await self._handle_connection_error(e)
                    break

        except asyncio.CancelledError:
            pass
        finally:
            logger.debug('Receive loop ended')

    async def _receive_pdu(self) -> Optional[PDU]:
        """Receive and decode a single PDU"""
        if not self._reader:
            return None

        try:
            # Read PDU header with a longer timeout for idle connections
            # Use a timeout that's longer than enquire_link_interval to avoid premature timeouts
            receive_timeout = max(self.read_timeout, self.enquire_link_interval + 10)
            header_data = await asyncio.wait_for(
                self._reader.readexactly(PDU_HEADER_SIZE), timeout=receive_timeout
            )

            if not header_data:
                raise SMPPConnectionException('Connection closed by peer')

            # Parse header to get total length
            length = struct.unpack('>L', header_data[:4])[0]
            command_id = struct.unpack('>L', header_data[4:8])[0]
            command_status = struct.unpack('>L', header_data[8:12])[0]
            sequence_number = struct.unpack('>L', header_data[12:16])[0]

            # Validate PDU structure - convert validation errors to PDU errors for compatibility
            try:
                validate_pdu_structure(
                    command_id, length, sequence_number, command_status
                )
            except SMPPValidationException as e:
                # Extract just the core message for compatibility
                if 'PDU length too small' in str(e):
                    raise SMPPPDUException(f'Invalid PDU length: {length}')
                else:
                    raise SMPPPDUException(f'Invalid PDU: {e}')

            if length < PDU_HEADER_SIZE:
                raise SMPPPDUException(f'Invalid PDU length: {length}')

            # Read remaining data
            remaining_length = length - PDU_HEADER_SIZE
            if remaining_length > 0:
                body_data = await asyncio.wait_for(
                    self._reader.readexactly(remaining_length),
                    timeout=receive_timeout,
                )
                full_data = header_data + body_data
            else:
                full_data = header_data

            # Decode PDU
            pdu = decode_pdu(full_data)
            self._last_activity = time.time()

            logger.debug(
                f'Received PDU: {pdu.__class__.__name__} (seq={pdu.sequence_number}, len={len(full_data)})'
            )
            return pdu

        except asyncio.TimeoutError:
            raise SMPPTimeoutException('PDU receive timeout')
        except asyncio.IncompleteReadError:
            raise SMPPConnectionException('Connection closed by peer')
        except Exception as e:
            if isinstance(
                e,
                (
                    SMPPConnectionException,
                    SMPPTimeoutException,
                    SMPPPDUException,
                    SMPPValidationException,
                ),
            ):
                raise
            raise SMPPConnectionException(f'Failed to receive PDU: {e}')

    async def _handle_received_pdu(self, pdu: PDU) -> None:
        """Handle received PDU"""
        # Check if this is a response to a pending request
        pending_entry = self._pending_pdus.get(pdu.sequence_number)
        if pending_entry and not pending_entry[0].done():
            pending_entry[0].set_result(pdu)
            self._pending_pdus.pop(pdu.sequence_number, None)
            return

        # Not a response, handle as incoming PDU
        if self.on_pdu_received:
            try:
                self.on_pdu_received(pdu)
            except Exception as e:
                logger.exception(f'Error in PDU received handler: {e}')

    async def _enquire_link_loop(self) -> None:
        """Background task to send periodic enquire_link PDUs"""
        logger.debug('Starting enquire_link loop')

        try:
            while self.is_connected:
                # Wait for the enquire_link interval
                await asyncio.sleep(self.enquire_link_interval)

                if not self.is_connected:
                    break

                # Send enquire_link to keep connection alive
                try:
                    logger.debug('Sending enquire_link')
                    enquire_link = EnquireLink()
                    await self.send_pdu(enquire_link, wait_response=True, timeout=10.0)
                except Exception as e:
                    logger.error(f'Enquire_link failed: {e}')
                    await self._handle_connection_error(e)
                    break

        except asyncio.CancelledError:
            pass
        finally:
            logger.debug('Enquire_link loop ended')

    async def _cleanup_loop(self) -> None:
        """Background task to clean up stale pending PDUs"""
        logger.debug('Starting cleanup loop')

        try:
            while self.is_connected:
                try:
                    # Clean up old pending PDUs
                    current_time = time.time()
                    stale_sequences = []

                    for seq, (future, timestamp) in self._pending_pdus.items():
                        if current_time - timestamp > self.read_timeout:
                            stale_sequences.append(seq)

                    futures_to_cleanup = []
                    for seq in stale_sequences:
                        pending_entry = self._pending_pdus.pop(seq, None)
                        if pending_entry:
                            future, _ = pending_entry
                            if future and not future.done():
                                future.set_exception(
                                    SMPPTimeoutException(
                                        f'PDU {seq} timed out during cleanup'
                                    )
                                )
                            futures_to_cleanup.append(future)

                    # Clean up futures to prevent warnings
                    for future in futures_to_cleanup:
                        try:
                            future.exception()
                        except Exception:
                            pass

                    if stale_sequences:
                        logger.debug(f'Cleaned up {len(stale_sequences)} stale PDUs')

                    # Check memory limits
                    self._check_memory_limits()

                    await asyncio.sleep(getattr(self, 'cleanup_interval', 60))

                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.exception(f'Error in cleanup loop: {e}')
                    await asyncio.sleep(5)

        except Exception as e:
            logger.exception(f'Cleanup loop error: {e}')

    async def _handle_connection_error(self, error: Exception) -> None:
        """Handle connection errors"""
        logger.error(f'Connection error: {error}')

        if self.on_connection_lost:
            try:
                self.on_connection_lost(error)
            except Exception as e:
                logger.exception(f'Error in connection lost handler: {e}')

        # Trigger disconnect, but avoid recursion if called from a background task
        current_task = asyncio.current_task()
        if current_task in (
            self._receive_task,
            self._enquire_link_task,
            self._cleanup_task,
        ):
            # Schedule disconnect in the next event loop iteration to avoid recursion
            asyncio.create_task(self.disconnect())
        else:
            await self.disconnect()

    def _check_memory_limits(self) -> None:
        """Check and enforce memory limits for pending PDUs"""
        if len(self._pending_pdus) > self.max_pending_pdus:
            # Remove oldest pending PDUs to prevent memory exhaustion
            oldest_items = sorted(
                self._pending_pdus.items(),
                key=lambda x: x[1][1],  # Sort by timestamp
            )

            # Remove enough items to get back under the limit
            remove_count = len(self._pending_pdus) - self.max_pending_pdus
            futures_to_cleanup = []
            for seq, (future, _) in oldest_items[:remove_count]:
                if not future.done():
                    future.set_exception(
                        SMPPConnectionException(
                            'PDU queue full, oldest requests cancelled'
                        )
                    )
                    futures_to_cleanup.append(future)
                # Remove from dict to prevent further access
                self._pending_pdus.pop(seq, None)

            # Clean up futures to prevent warnings
            for future in futures_to_cleanup:
                try:
                    future.exception()
                except Exception:
                    pass

            logger.warning(
                f'Removed {remove_count} pending PDUs due to memory limits '
                f'({len(self._pending_pdus)}/{self.max_pending_pdus})'
            )

    def set_bound_state(self, bind_type: str) -> None:
        """Set bound state based on bind type"""
        state_map = {
            'transmitter': ConnectionState.BOUND_TX,
            'receiver': ConnectionState.BOUND_RX,
            'transceiver': ConnectionState.BOUND_TRX,
        }

        new_state = state_map.get(bind_type.lower())
        if new_state:
            self._set_state(new_state)
        else:
            logger.warning(f'Unknown bind type: {bind_type}')

    def __repr__(self) -> str:
        return f'SMPPConnection(host={self.host}, port={self.port}, state={self._state.value})'

    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()
