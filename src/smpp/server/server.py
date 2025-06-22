"""
SMPP Server (SMSC) Implementation

This module provides a basic SMPP server implementation that can be used
for testing SMPP clients or as a foundation for building custom SMSC solutions.
"""

import asyncio
import logging
import signal
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional

from ..exceptions import SMPPException
from ..protocol import (
    PDU,
    BindReceiver,
    BindReceiverResp,
    BindTransceiver,
    BindTransceiverResp,
    BindTransmitter,
    BindTransmitterResp,
    CommandStatus,
    DataCoding,
    DeliverSm,
    DeliverSmResp,
    EnquireLink,
    EnquireLinkResp,
    GenericNack,
    NpiType,
    SubmitSm,
    SubmitSmResp,
    TonType,
    Unbind,
    UnbindResp,
    get_error_message,
)
from ..transport import ConnectionState, SMPPConnection

logger = logging.getLogger(__name__)


@dataclass
class ClientSession:
    """Represents a connected SMPP client session"""

    connection: SMPPConnection
    system_id: str = ''
    bind_type: str = ''
    bound: bool = False
    address_range: str = ''
    message_counter: int = 0


class SMPPServer:
    """
    Async SMPP Server (SMSC) Implementation

    Provides a basic SMPP server that can handle client connections,
    bind operations, and message submission/delivery.
    """

    def __init__(
        self,
        host: str = 'localhost',
        port: int = 2775,
        system_id: str = 'SMSC',
        interface_version: int = 0x34,
        max_connections: int = 100,
    ):
        """
        Initialize SMPP Server

        Args:
            host: Server bind address
            port: Server bind port
            system_id: Server system ID
            interface_version: SMPP interface version
            max_connections: Maximum concurrent connections
        """
        self.host = host
        self.port = port
        self.system_id = system_id
        self.interface_version = interface_version
        self.max_connections = max_connections

        self._server: Optional[asyncio.Server] = None
        self._running = False
        self._clients: Dict[str, ClientSession] = {}
        self._message_id_counter = 1
        self._shutdown_event = asyncio.Event()
        self._shutdown_timeout = 30.0  # seconds to wait for graceful shutdown
        self._shutdown_in_progress = False  # Flag to prevent multiple shutdowns

        # Authentication callback - should return True if credentials are valid
        self.authenticate: Optional[Callable[[str, str, str], bool]] = None

        # Event handlers
        self.on_client_connected: Optional[
            Callable[['SMPPServer', ClientSession], None]
        ] = None
        self.on_client_disconnected: Optional[
            Callable[['SMPPServer', ClientSession], None]
        ] = None
        self.on_client_bound: Optional[
            Callable[['SMPPServer', ClientSession], None]
        ] = None
        self.on_message_received: Optional[
            Callable[['SMPPServer', ClientSession, SubmitSm], Optional[str]]
        ] = None

        # Default authentication (allows all)
        self.authenticate = self._default_authenticate

    def set_shutdown_timeout(self, timeout: float) -> None:
        """
        Set the timeout for graceful shutdown.

        Args:
            timeout: Maximum time in seconds to wait for clients to disconnect
        """
        self._shutdown_timeout = max(0.0, timeout)
        logger.debug(f'Shutdown timeout set to {self._shutdown_timeout}s')

    def _default_authenticate(
        self, system_id: str, password: str, system_type: str
    ) -> bool:
        """Default authentication - allows all connections"""
        logger.info(
            f'Authenticating client: system_id={system_id}, system_type={system_type}'
        )
        return True

    @property
    def is_running(self) -> bool:
        """Check if server is running"""
        return self._running and self._server is not None

    @property
    def shutdown_requested(self) -> bool:
        """Check if shutdown has been requested"""
        return self._shutdown_event.is_set() or self._shutdown_in_progress

    @property
    def client_count(self) -> int:
        """Get number of connected clients"""
        return len(self._clients)

    async def start(self) -> None:
        """Start the SMPP server"""
        if self.is_running:
            raise SMPPException('Server is already running')

        logger.info(f'Starting SMPP server on {self.host}:{self.port}')

        self._server = await asyncio.start_server(
            self._handle_client_connection, self.host, self.port
        )

        self._running = True

        # Set up signal handlers for graceful shutdown
        self._setup_signal_handlers()

        logger.info(f'SMPP server started on {self.host}:{self.port}')

    async def stop(self) -> None:
        """Stop the SMPP server gracefully"""
        if not self.is_running or self._shutdown_in_progress:
            return

        self._shutdown_in_progress = True
        logger.info('Initiating graceful shutdown of SMPP server')
        self._running = False

        try:
            # Stop accepting new connections
            if self._server:
                self._server.close()
                await self._server.wait_closed()
                self._server = None
                logger.info('Server stopped accepting new connections')

            # Gracefully disconnect all clients
            await self._graceful_client_shutdown()

        except Exception as e:
            logger.error(f'Error during server shutdown: {e}')
        finally:
            self._clients.clear()
            self._shutdown_in_progress = False
            logger.info('SMPP server stopped')

    def _setup_signal_handlers(self) -> None:
        """Set up signal handlers for graceful shutdown"""
        try:
            def signal_handler(signum, frame):
                if not self._shutdown_event.is_set():
                    logger.info(f'Received signal {signum}, initiating graceful shutdown')
                    self._shutdown_event.set()
                else:
                    logger.info(f'Received signal {signum}, shutdown already in progress')

            # Set up handlers for common shutdown signals
            for sig in [signal.SIGTERM, signal.SIGINT]:
                try:
                    signal.signal(sig, signal_handler)
                    logger.debug(f'Signal handler registered for {sig}')
                except (ValueError, OSError) as e:
                    # This can happen in threads or Windows
                    logger.debug(f'Could not register signal handler for {sig}: {e}')

        except Exception as e:
            logger.debug(f'Could not set up signal handlers: {e}')

    async def _graceful_client_shutdown(self) -> None:
        """Gracefully disconnect all clients"""
        if not self._clients:
            return

        logger.info(f'Disconnecting {len(self._clients)} clients gracefully')

        # Send unbind requests to all bound clients
        unbind_tasks = []
        for client in list(self._clients.values()):
            if client.bound:
                task = asyncio.create_task(self._send_unbind_to_client(client))
                unbind_tasks.append(task)

        # Wait for unbind responses with timeout
        if unbind_tasks:
            try:
                await asyncio.wait_for(
                    asyncio.gather(*unbind_tasks, return_exceptions=True),
                    timeout=10.0
                )
                logger.info('Sent unbind requests to all bound clients')
            except asyncio.TimeoutError:
                logger.warning('Timeout waiting for unbind responses')

        # Force disconnect remaining clients
        disconnect_tasks = []
        for client in list(self._clients.values()):
            try:
                task = asyncio.create_task(client.connection.disconnect())
                disconnect_tasks.append(task)
            except Exception as e:
                logger.warning(f'Error creating disconnect task for client: {e}')

        # Wait for all disconnections with timeout
        if disconnect_tasks:
            try:
                await asyncio.wait_for(
                    asyncio.gather(*disconnect_tasks, return_exceptions=True),
                    timeout=self._shutdown_timeout
                )
                logger.info('All clients disconnected')
            except asyncio.TimeoutError:
                logger.warning(f'Timeout after {self._shutdown_timeout}s waiting for client disconnections')

    async def _send_unbind_to_client(self, client: ClientSession) -> None:
        """Send unbind request to a client"""
        try:
            if client.connection and client.bound:
                # Create unbind PDU
                unbind_pdu = Unbind()

                # Send unbind and wait for response
                await client.connection.send_pdu(unbind_pdu, wait_response=True, timeout=5.0)
                logger.debug(f'Sent unbind to client {client.system_id}')

                # Update client state
                client.bound = False
                client.bind_type = ''

        except Exception as e:
            logger.warning(f'Error sending unbind to client {client.system_id}: {e}')

    async def _handle_client_connection(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        """Handle new client connection"""
        client_addr = writer.get_extra_info('peername')
        logger.info(f'New client connection from {client_addr}')

        if len(self._clients) >= self.max_connections:
            logger.warning(f'Maximum connections exceeded, rejecting {client_addr}')
            writer.close()
            await writer.wait_closed()
            return

        # Create connection and session
        connection = SMPPConnection(
            host=client_addr[0] if client_addr else 'unknown',
            port=client_addr[1] if client_addr else 0,
            reader=reader,
            writer=writer,
        )

        session = ClientSession(connection=connection)
        client_id = f'{client_addr[0]}:{client_addr[1]}' if client_addr else 'unknown'
        self._clients[client_id] = session

        # Set up connection handlers
        connection.on_pdu_received = lambda pdu: self._handle_client_pdu(session, pdu)

        def handle_connection_lost(error):
            asyncio.create_task(self._handle_client_disconnected(session, error))

        connection.on_connection_lost = handle_connection_lost

        # Mark connection as established
        connection._connected = True
        connection._set_state(ConnectionState.OPEN)

        # Start receive loop
        connection._receive_task = asyncio.create_task(connection._receive_loop())

        # Trigger client connected event
        if self.on_client_connected:
            try:
                self.on_client_connected(self, session)
            except Exception as e:
                logger.exception(f'Error in client connected handler: {e}')

        logger.info(f'Client {client_id} connected')

    async def _handle_client_disconnected(
        self, session: ClientSession, error: Exception
    ) -> None:
        """Handle client disconnection"""
        client_id = None

        # Find and remove client
        for cid, client in list(self._clients.items()):
            if client is session:
                client_id = cid
                del self._clients[cid]
                break

        logger.info(f'Client {client_id or "unknown"} disconnected: {error}')

        # Trigger client disconnected event
        if self.on_client_disconnected:
            try:
                self.on_client_disconnected(self, session)
            except Exception as e:
                logger.exception(f'Error in client disconnected handler: {e}')

    def _handle_client_pdu(self, session: ClientSession, pdu: PDU) -> None:
        """Handle PDU received from client"""
        try:
            logger.debug(
                f'Received PDU from {session.system_id}: {pdu.__class__.__name__}'
            )

            if isinstance(pdu, (BindTransmitter, BindReceiver, BindTransceiver)):
                asyncio.create_task(self._handle_bind_request(session, pdu))
            elif isinstance(pdu, Unbind):
                asyncio.create_task(self._handle_unbind_request(session, pdu))
            elif isinstance(pdu, SubmitSm):
                asyncio.create_task(self._handle_submit_sm(session, pdu))
            elif isinstance(pdu, EnquireLink):
                asyncio.create_task(self._handle_enquire_link(session, pdu))
            elif isinstance(pdu, DeliverSmResp):
                # Acknowledge delivery receipt
                logger.debug(f'Received deliver_sm_resp from {session.system_id}')
            else:
                logger.warning(f'Unhandled PDU type: {pdu.__class__.__name__}')
                asyncio.create_task(
                    self._send_generic_nack(
                        session, pdu.sequence_number, CommandStatus.ESME_RINVCMDID
                    )
                )

        except Exception as e:
            logger.exception(f'Error handling PDU from {session.system_id}: {e}')
            asyncio.create_task(
                self._send_generic_nack(
                    session, pdu.sequence_number, CommandStatus.ESME_RUNKNOWNERR
                )
            )

    async def _handle_bind_request(self, session: ClientSession, pdu: PDU) -> None:
        """Handle bind request from client"""
        try:
            # Cast to specific bind PDU type to access attributes
            if isinstance(pdu, (BindTransmitter, BindReceiver, BindTransceiver)):
                bind_pdu = pdu
            else:
                logger.error(f'Invalid PDU type for bind request: {type(pdu)}')
                return

            system_id = bind_pdu.system_id
            password = bind_pdu.password
            system_type = bind_pdu.system_type

            logger.info(
                f'Bind request from {system_id} (type: {pdu.__class__.__name__})'
            )

            # Check if already bound
            if session.bound:
                await self._send_bind_response(session, pdu, CommandStatus.ESME_RALYBND)
                return

            # Authenticate client
            if self.authenticate and not self.authenticate(
                system_id, password, system_type
            ):
                logger.warning(f'Authentication failed for {system_id}')
                await self._send_bind_response(
                    session, pdu, CommandStatus.ESME_RBINDFAIL
                )
                return

            # Update session
            session.system_id = system_id
            session.address_range = pdu.address_range
            session.bound = True

            if isinstance(pdu, BindTransmitter):
                session.bind_type = 'transmitter'
                session.connection.set_bound_state('transmitter')
            elif isinstance(pdu, BindReceiver):
                session.bind_type = 'receiver'
                session.connection.set_bound_state('receiver')
            elif isinstance(pdu, BindTransceiver):
                session.bind_type = 'transceiver'
                session.connection.set_bound_state('transceiver')

            # Send success response
            await self._send_bind_response(session, pdu, CommandStatus.ESME_ROK)

            logger.info(f'Client {system_id} bound as {session.bind_type}')

            # Trigger client bound event
            if self.on_client_bound:
                try:
                    self.on_client_bound(self, session)
                except Exception as e:
                    logger.exception(f'Error in client bound handler: {e}')

        except Exception as e:
            logger.exception(f'Error handling bind request: {e}')
            await self._send_bind_response(session, pdu, CommandStatus.ESME_RBINDFAIL)

    async def _send_bind_response(
        self, session: ClientSession, bind_pdu: PDU, status: CommandStatus
    ) -> None:
        """Send bind response to client"""
        try:
            # Create appropriate response PDU
            resp_pdu: Optional[PDU] = None
            if isinstance(bind_pdu, BindTransmitter):
                resp_pdu = BindTransmitterResp(  # type: ignore[call-arg]
                    sequence_number=bind_pdu.sequence_number,
                    command_status=status,
                    system_id=self.system_id  # type: ignore[call-arg]
                    if status == CommandStatus.ESME_ROK
                    else '',
                )
            elif isinstance(bind_pdu, BindReceiver):
                resp_pdu = BindReceiverResp(  # type: ignore[call-arg]
                    sequence_number=bind_pdu.sequence_number,
                    command_status=status,
                    system_id=self.system_id  # type: ignore[call-arg]
                    if status == CommandStatus.ESME_ROK
                    else '',
                )
            elif isinstance(bind_pdu, BindTransceiver):
                resp_pdu = BindTransceiverResp(  # type: ignore[call-arg]
                    sequence_number=bind_pdu.sequence_number,
                    command_status=status,
                    system_id=self.system_id  # type: ignore[call-arg]
                    if status == CommandStatus.ESME_ROK
                    else '',
                )
            else:
                return

            if resp_pdu:
                await session.connection.send_pdu(resp_pdu, wait_response=False)

        except Exception as e:
            logger.error(f'Failed to send bind response: {e}')

    async def _handle_unbind_request(self, session: ClientSession, pdu: Unbind) -> None:
        """Handle unbind request from client"""
        try:
            logger.info(f'Unbind request from {session.system_id}')

            # Send unbind response
            resp_pdu = UnbindResp(
                sequence_number=pdu.sequence_number,
                command_status=CommandStatus.ESME_ROK,
            )
            await session.connection.send_pdu(resp_pdu, wait_response=False)

            # Update session state
            session.bound = False
            session.bind_type = ''

            # Disconnect client
            await session.connection.disconnect()

        except Exception as e:
            logger.error(f'Error handling unbind request: {e}')

    async def _handle_submit_sm(self, session: ClientSession, pdu: SubmitSm) -> None:
        """Handle submit_sm request from client"""
        try:
            if not session.bound or session.bind_type not in (
                'transmitter',
                'transceiver',
            ):
                await self._send_submit_sm_response(
                    session, pdu, CommandStatus.ESME_RINVBNDSTS
                )
                return

            logger.info(
                f'Message from {session.system_id}: {pdu.source_addr} -> {pdu.destination_addr}'
            )

            # Generate message ID
            message_id = self._get_next_message_id()

            # Call message received handler if set
            custom_message_id = None
            if self.on_message_received:
                try:
                    custom_message_id = self.on_message_received(self, session, pdu)
                except Exception as e:
                    logger.exception(f'Error in message received handler: {e}')

            # Use custom message ID if provided
            if custom_message_id:
                message_id = custom_message_id

            # Send success response
            await self._send_submit_sm_response(
                session, pdu, CommandStatus.ESME_ROK, message_id
            )

            session.message_counter += 1
            logger.debug(f'Message accepted, assigned ID: {message_id}')

        except Exception as e:
            logger.exception(f'Error handling submit_sm: {e}')
            await self._send_submit_sm_response(
                session, pdu, CommandStatus.ESME_RSUBMITFAIL
            )

    async def _send_submit_sm_response(
        self,
        session: ClientSession,
        submit_pdu: SubmitSm,
        status: CommandStatus,
        message_id: str = '',
    ) -> None:
        """Send submit_sm response to client"""
        try:
            resp_pdu = SubmitSmResp(
                sequence_number=submit_pdu.sequence_number,
                command_status=status,
                message_id=message_id,
            )
            await session.connection.send_pdu(resp_pdu, wait_response=False)

        except Exception as e:
            logger.error(f'Failed to send submit_sm response: {e}')

    async def _handle_enquire_link(
        self, session: ClientSession, pdu: EnquireLink
    ) -> None:
        """Handle enquire_link request from client"""
        try:
            resp_pdu = EnquireLinkResp(
                sequence_number=pdu.sequence_number,
                command_status=CommandStatus.ESME_ROK,
            )
            await session.connection.send_pdu(resp_pdu, wait_response=False)

        except Exception as e:
            logger.error(f'Failed to send enquire_link response: {e}')

    async def _send_generic_nack(
        self, session: ClientSession, sequence_number: int, status: CommandStatus
    ) -> None:
        """Send generic_nack to client"""
        try:
            nack_pdu = GenericNack(
                sequence_number=sequence_number, command_status=status
            )
            await session.connection.send_pdu(nack_pdu, wait_response=False)

        except Exception as e:
            logger.error(f'Failed to send generic_nack: {e}')

    async def deliver_sm(
        self,
        target_system_id: str,
        source_addr: str,
        destination_addr: str,
        short_message: str,
        source_addr_ton: int = TonType.UNKNOWN,
        source_addr_npi: int = NpiType.UNKNOWN,
        dest_addr_ton: int = TonType.UNKNOWN,
        dest_addr_npi: int = NpiType.UNKNOWN,
        service_type: str = '',
        esm_class: int = 0,
        protocol_id: int = 0,
        priority_flag: int = 0,
        data_coding: int = DataCoding.DEFAULT,
    ) -> bool:
        """
        Deliver SMS message to a specific client

        Args:
            target_system_id: Target client system ID
            source_addr: Source address
            destination_addr: Destination address
            short_message: Message text
            ... (other parameters as in submit_sm)

        Returns:
            True if message was delivered successfully, False otherwise
        """
        # Find target client
        target_session = None
        for session in self._clients.values():
            if session.system_id == target_system_id and session.bound:
                if session.bind_type in ('receiver', 'transceiver'):
                    target_session = session
                    break

        if not target_session:
            logger.warning(
                f'Target client not found or not bound as receiver: {target_system_id}'
            )
            return False

        try:
            # Encode message
            message_bytes = short_message.encode('utf-8')

            # Create deliver_sm PDU
            deliver_pdu = DeliverSm(  # type: ignore[call-arg]
                service_type=service_type,
                source_addr_ton=source_addr_ton,
                source_addr_npi=source_addr_npi,
                source_addr=source_addr,
                dest_addr_ton=dest_addr_ton,
                dest_addr_npi=dest_addr_npi,
                destination_addr=destination_addr,
                esm_class=esm_class,
                protocol_id=protocol_id,
                priority_flag=priority_flag,
                schedule_delivery_time='',
                validity_period='',
                registered_delivery=0,
                replace_if_present_flag=0,
                data_coding=data_coding,
                sm_default_msg_id=0,
                short_message=message_bytes,
            )

            # Send deliver_sm and wait for response
            response = await target_session.connection.send_pdu(
                deliver_pdu, wait_response=True, timeout=30.0
            )

            if response and response.command_status == CommandStatus.ESME_ROK:
                logger.info(
                    f'Message delivered to {target_system_id}: {source_addr} -> {destination_addr}'
                )
                return True
            else:
                error_msg = (
                    get_error_message(response.command_status)
                    if response
                    else 'No response received'
                )
                logger.warning(
                    f'Message delivery failed to {target_system_id}: {error_msg}'
                )
                return False

        except Exception as e:
            logger.error(f'Error delivering message to {target_system_id}: {e}')
            return False

    def _get_next_message_id(self) -> str:
        """Generate next message ID"""
        msg_id = str(self._message_id_counter)
        self._message_id_counter += 1
        return msg_id

    async def serve_forever(self) -> None:
        """
        Start the server and run until shutdown signal is received.

        This method handles graceful shutdown when SIGTERM or SIGINT is received.
        """
        await self.start()

        try:
            logger.info('Server running, waiting for shutdown signal...')
            # Wait for shutdown signal
            await self._shutdown_event.wait()
            logger.info('Shutdown signal received, stopping server...')
        except KeyboardInterrupt:
            logger.info('Keyboard interrupt received')
        finally:
            await self.stop()

    def get_client_sessions(self) -> List[ClientSession]:
        """Get list of all client sessions"""
        return list(self._clients.values())

    def get_bound_clients(self) -> List[ClientSession]:
        """Get list of bound client sessions"""
        return [session for session in self._clients.values() if session.bound]

    async def __aenter__(self):
        """Async context manager entry"""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit with graceful shutdown"""
        if exc_type is KeyboardInterrupt:
            logger.info('KeyboardInterrupt in context manager, shutting down gracefully')
        await self.stop()

    def __repr__(self) -> str:
        return f'SMPPServer(host={self.host}, port={self.port}, clients={self.client_count})'
