"""
SMPP Client (ESME) Implementation

This module provides a comprehensive async SMPP client implementation
that can connect to SMSC servers and perform SMS operations.
"""

import asyncio
import logging
import time
from enum import Enum
from typing import Callable, List, Optional

from ..exceptions import (
    SMPPBindException,
    SMPPConnectionException,
    SMPPException,
    SMPPInvalidStateException,
    SMPPMessageException,
    SMPPPDUException,
    SMPPThrottlingException,
    SMPPTimeoutException,
    SMPPValidationException,
)
from ..gsm import make_parts
from ..protocol import (
    PDU,
    BindReceiver,
    BindTransceiver,
    BindTransmitter,
    CancelSm,
    CommandId,
    CommandStatus,
    DataCoding,
    DataSm,
    DataSmResp,
    DeliverSm,
    DeliverSmResp,
    EnquireLink,
    EnquireLinkResp,
    NpiType,
    OptionalTag,
    QuerySm,
    QuerySmResp,
    RegisteredDelivery,
    ReplaceSm,
    SubmitSm,
    TonType,
    Unbind,
    UnbindResp,
    encode_message_with_encoding,
    get_error_message,
)
from ..protocol.constants import DEFAULT_INTERFACE_VERSION, MAX_SHORT_MESSAGE_LENGTH
from ..transport import ConnectionState, SMPPConnection

logger = logging.getLogger(__name__)

# SMSC "can't take it now" statuses: callers should back off and retry.
_THROTTLE_STATUSES = (CommandStatus.ESME_RTHROTTLED, CommandStatus.ESME_RMSGQFUL)


class BindType(Enum):
    """SMPP Bind Types"""

    TRANSMITTER = 'transmitter'
    RECEIVER = 'receiver'
    TRANSCEIVER = 'transceiver'


class SMPPClient:
    """
    Async SMPP Client (ESME) Implementation

    Provides a high-level interface for connecting to SMSC servers,
    sending SMS messages, and handling delivery receipts.
    """

    def __init__(
        self,
        host: str,
        port: int,
        system_id: str,
        password: str,
        system_type: str = '',
        interface_version: int = DEFAULT_INTERFACE_VERSION,
        addr_ton: int = TonType.UNKNOWN,
        addr_npi: int = NpiType.UNKNOWN,
        address_range: str = '',
        bind_timeout: float = 30.0,
        enquire_link_interval: float = 60.0,
        response_timeout: float = 30.0,
    ):
        """
        Initialize SMPP Client

        Args:
            host: SMSC server hostname or IP
            port: SMSC server port
            system_id: System ID for authentication
            password: Password for authentication
            system_type: System type identifier
            interface_version: SMPP interface version
            addr_ton: Address Type of Number
            addr_npi: Address Numbering Plan Indicator
            address_range: Address range for receiver binding
            bind_timeout: Timeout for bind operations
            enquire_link_interval: Interval for enquire_link keepalive
            response_timeout: Default timeout for responses
        """
        self.host = host
        self.port = port
        self.system_id = system_id
        self.password = password
        self.system_type = system_type
        self.interface_version = interface_version
        self.addr_ton = addr_ton
        self.addr_npi = addr_npi
        self.address_range = address_range
        self.bind_timeout = bind_timeout
        self.response_timeout = response_timeout

        self._connection: Optional[SMPPConnection] = None
        self._bind_type: Optional[BindType] = None
        self.sc_interface_version: Optional[int] = None
        self._bound = False

        # Event handlers
        self.on_deliver_sm: Optional[Callable[['SMPPClient', DeliverSm], None]] = None
        self.on_data_sm: Optional[Callable[['SMPPClient', DataSm], None]] = None
        self.on_connection_lost: Optional[Callable[['SMPPClient', Exception], None]] = (
            None
        )
        self.on_bind_success: Optional[Callable[['SMPPClient', BindType], None]] = None
        self.on_unbind: Optional[Callable[['SMPPClient'], None]] = None

        # Create connection
        self._connection = SMPPConnection(
            host=host,
            port=port,
            enquire_link_interval=enquire_link_interval,
            read_timeout=response_timeout,
            write_timeout=response_timeout,
        )

        # Set connection event handlers
        self._connection.on_pdu_received = self._handle_pdu_received
        self._connection.on_connection_lost = self._handle_connection_lost

    @property
    def is_connected(self) -> bool:
        """Check if client is connected to SMSC"""
        return self._connection is not None and self._connection.is_connected

    @property
    def is_bound(self) -> bool:
        """Check if client is bound to SMSC"""
        return self._bound and self.is_connected

    @property
    def bind_type(self) -> Optional[BindType]:
        """Get current bind type"""
        return self._bind_type

    @property
    def connection_state(self) -> ConnectionState:
        """Get connection state"""
        return self._connection.state if self._connection else ConnectionState.CLOSED

    async def connect(self) -> None:
        """Connect to SMSC server"""
        if not self._connection:
            raise SMPPException('Connection not initialized')

        if self.is_connected:
            raise SMPPConnectionException('Already connected')

        logger.info(f'Connecting to SMSC at {self.host}:{self.port}')
        await self._connection.connect()
        logger.info('Connected to SMSC')

    async def disconnect(self) -> None:
        """Disconnect from SMSC server"""
        if not self.is_connected:
            return

        logger.info('Disconnecting from SMSC')

        # Unbind if bound
        if self.is_bound:
            try:
                await self.unbind()
            except Exception as e:
                logger.warning(f'Error during unbind: {e}')

        # Close connection
        if self._connection:
            await self._connection.disconnect()

        self._bound = False
        self._bind_type = None
        self.sc_interface_version = None
        logger.info('Disconnected from SMSC')

    async def bind_transmitter(self) -> None:
        """Bind as transmitter (can send SMS)"""
        await self._bind(BindType.TRANSMITTER)

    async def bind_receiver(self) -> None:
        """Bind as receiver (can receive SMS and delivery receipts)"""
        await self._bind(BindType.RECEIVER)

    async def bind_transceiver(self) -> None:
        """Bind as transceiver (can send and receive SMS)"""
        await self._bind(BindType.TRANSCEIVER)

    async def _bind(self, bind_type: BindType) -> None:
        """Perform bind operation"""
        if not self.is_connected:
            raise SMPPInvalidStateException('Not connected to SMSC')

        if self.is_bound:
            raise SMPPInvalidStateException('Already bound')

        logger.info(f'Binding as {bind_type.value}')

        # Create appropriate bind PDU
        bind_pdu_map = {
            BindType.TRANSMITTER: BindTransmitter,
            BindType.RECEIVER: BindReceiver,
            BindType.TRANSCEIVER: BindTransceiver,
        }

        bind_pdu_class = bind_pdu_map[bind_type]
        bind_pdu = bind_pdu_class(  # type: ignore[call-arg]
            system_id=self.system_id,
            password=self.password,
            system_type=self.system_type,
            interface_version=self.interface_version,
            addr_ton=self.addr_ton,
            addr_npi=self.addr_npi,
            address_range=self.address_range,
        )

        try:
            # Send bind request and wait for response
            if self._connection is None:
                raise SMPPBindException('Not connected to server')

            response = await self._connection.send_pdu(
                bind_pdu, wait_response=True, timeout=self.bind_timeout
            )

            if response is None:
                raise SMPPBindException('No response received from server')

            if response.command_status != CommandStatus.ESME_ROK:
                error_msg = get_error_message(response.command_status)
                raise SMPPBindException(
                    f'Bind failed: {error_msg}',
                    bind_type=bind_type.value,
                    command_status=response.command_status,
                    pdu=response,
                )

            # Update state
            self._bound = True
            self._bind_type = bind_type
            try:
                tlv = response.get_tlv(OptionalTag.SC_INTERFACE_VERSION)
            except SMPPValidationException:
                tlv = None
            self.sc_interface_version = tlv if isinstance(tlv, int) else None
            self._connection.set_bound_state(bind_type.value)

            logger.info(f'Successfully bound as {bind_type.value}')

            # Trigger bind success event
            if self.on_bind_success:
                try:
                    self.on_bind_success(self, bind_type)
                except Exception as e:
                    logger.exception(f'Error in bind success handler: {e}')

        except SMPPTimeoutException:
            raise SMPPBindException(
                f'Bind timeout after {self.bind_timeout} seconds',
                bind_type=bind_type.value,
            )
        except Exception as e:
            if isinstance(e, SMPPBindException):
                raise
            raise SMPPBindException(f'Bind failed: {e}', bind_type=bind_type.value)

    async def unbind(self) -> None:
        """Unbind from SMSC"""
        if not self.is_bound:
            raise SMPPInvalidStateException('Not bound')

        logger.info('Unbinding from SMSC')

        try:
            unbind_pdu = Unbind()

            if self._connection is None:
                logger.warning('Not connected, cannot send unbind')
                return

            response = await self._connection.send_pdu(
                unbind_pdu, wait_response=True, timeout=self.response_timeout
            )

            if (
                response is not None
                and response.command_status != CommandStatus.ESME_ROK
            ):
                logger.warning(
                    f'Unbind response error: {get_error_message(response.command_status)}'
                )

        except Exception as e:
            logger.warning(f'Error during unbind: {e}')
        finally:
            self._bound = False
            self._bind_type = None
            self.sc_interface_version = None
            logger.info('Unbound from SMSC')

            # Trigger unbind event
            if self.on_unbind:
                try:
                    self.on_unbind(self)
                except Exception as e:
                    logger.exception(f'Error in unbind handler: {e}')

    async def submit_sm(
        self,
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
        schedule_delivery_time: str = '',
        validity_period: str = '',
        registered_delivery: int = RegisteredDelivery.NO_RECEIPT,
        replace_if_present_flag: int = 0,
        data_coding: int = DataCoding.DEFAULT,
        sm_default_msg_id: int = 0,
        timeout: Optional[float] = None,
    ) -> str:
        """
        Submit SMS message

        Args:
            source_addr: Source address (sender)
            destination_addr: Destination address (recipient)
            short_message: Message text
            source_addr_ton: Source address Type of Number
            source_addr_npi: Source address Numbering Plan Indicator
            dest_addr_ton: Destination address Type of Number
            dest_addr_npi: Destination address Numbering Plan Indicator
            service_type: Service type
            esm_class: ESM class
            protocol_id: Protocol ID
            priority_flag: Priority flag
            schedule_delivery_time: Scheduled delivery time
            validity_period: Message validity period
            registered_delivery: Registered delivery flag
            replace_if_present_flag: Replace if present flag
            data_coding: Data coding scheme
            sm_default_msg_id: Default message ID
            timeout: Response timeout

        Returns:
            Message ID assigned by SMSC

        Raises:
            SMPPInvalidStateException: If not bound as transmitter or transceiver
            SMPPMessageException: If message submission fails
        """
        self._require_tx_bind()

        logger.debug('Submitting SMS from %s to %s', source_addr, destination_addr)

        # Create submit_sm PDU
        submit_pdu = SubmitSm(  # type: ignore[call-arg]
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
            schedule_delivery_time=schedule_delivery_time,
            validity_period=validity_period,
            registered_delivery=registered_delivery,
            replace_if_present_flag=replace_if_present_flag,
            data_coding=data_coding,
            sm_default_msg_id=sm_default_msg_id,
        )
        try:
            submit_pdu.set_message_text(short_message)
        except UnicodeEncodeError as e:
            raise SMPPMessageException(
                f'Message not encodable with data_coding {data_coding:#x}; use DataCoding.UCS2'
            ) from e
        except SMPPPDUException as e:
            raise SMPPMessageException(str(e)) from e
        if len(submit_pdu.short_message) > MAX_SHORT_MESSAGE_LENGTH:
            raise SMPPMessageException(
                f'Message too long: {len(submit_pdu.short_message)} bytes'
            )

        return await self._send_submit(submit_pdu, timeout)

    def _require_tx_bind(self) -> None:
        """Raise SMPPInvalidStateException unless bound as transmitter or transceiver."""
        if not self.is_bound:
            raise SMPPInvalidStateException('Not bound to SMSC')

        if self._bind_type is None or self._bind_type not in (
            BindType.TRANSMITTER,
            BindType.TRANSCEIVER,
        ):
            bind_type_str = self._bind_type.value if self._bind_type else 'unknown'
            raise SMPPInvalidStateException(
                f'Cannot send SMS with bind type {bind_type_str}',
                current_state=bind_type_str,
                expected_state='transmitter or transceiver',
            )

    async def _send_submit(
        self, pdu: SubmitSm | DataSm, timeout: Optional[float]
    ) -> str:
        """Send a built submit_sm/data_sm PDU and wait for its response message_id."""
        try:
            if self._connection is None:
                raise SMPPMessageException('Not connected to SMSC')

            response = await self._connection.send_pdu(
                pdu, wait_response=True, timeout=timeout or self.response_timeout
            )

            if response is None:
                raise SMPPMessageException('No response received from SMSC')

            if response.command_status != CommandStatus.ESME_ROK:
                error_msg = get_error_message(response.command_status)
                exc_type = (
                    SMPPThrottlingException
                    if response.command_status in _THROTTLE_STATUSES
                    else SMPPMessageException
                )
                raise exc_type(
                    f'Message submission failed: {error_msg}',
                    command_status=response.command_status,
                    pdu=response,
                )

            message_id = response.message_id  # type: ignore[attr-defined]
            logger.debug('SMS submitted successfully, message_id: %s', message_id)
            return str(message_id) if message_id is not None else ''

        except SMPPTimeoutException:
            raise SMPPMessageException('Message submission timeout')
        except Exception as e:
            if isinstance(e, SMPPMessageException):
                raise
            raise SMPPMessageException(f'Message submission failed: {e}')

    async def submit_multipart(
        self,
        source_addr: str,
        destination_addr: str,
        message: str,
        *,
        data_coding: int = DataCoding.DEFAULT,
        esm_class: int = 0,
        registered_delivery: int = RegisteredDelivery.NO_RECEIPT,
        timeout: Optional[float] = None,
        **submit_kwargs,
    ) -> List[str]:
        """
        Submit a message as one or more concatenated (UDH) SMS parts.

        Splits `message` with smpp.gsm.make_parts and sends each part
        through the same submission path as submit_sm, sequentially,
        stopping at the first failure. submit_sm itself is unchanged; use
        this whenever the message might not fit a single segment.

        Args:
            source_addr: Source address (sender)
            destination_addr: Destination address (recipient)
            message: Message text to split and send
            data_coding: Data coding scheme, applied to every part
            esm_class: Base ESM class (the UDH indicator bit is added
                automatically for multi-part messages)
            registered_delivery: Registered delivery flag, applied to every part
            timeout: Response timeout per part
            **submit_kwargs: Remaining submit_sm fields (e.g. source_addr_ton,
                source_addr_npi, dest_addr_ton, dest_addr_npi, service_type,
                protocol_id, priority_flag, schedule_delivery_time,
                validity_period, replace_if_present_flag, sm_default_msg_id)

        Returns:
            One SMSC message_id per part, in part order. A message that fits
            one segment returns a list of length 1.

        Raises:
            SMPPInvalidStateException: If not bound as transmitter or transceiver
            SMPPMessageException: If the message can't be encoded with
                data_coding (raised before any part is sent), or a part's
                submission fails; a submission failure carries
                `.sent_message_ids`, the ids of parts already accepted
            ValueError: If the message needs more than 255 parts
        """
        self._require_tx_bind()

        try:
            parts = make_parts(message, data_coding)
        except SMPPPDUException as e:
            raise SMPPMessageException(str(e)) from e

        message_ids: List[str] = []
        for part in parts:
            submit_pdu = SubmitSm(  # type: ignore[call-arg]
                source_addr=source_addr,
                destination_addr=destination_addr,
                short_message=part.get_short_message(),
                esm_class=part.get_esm_class(esm_class),
                data_coding=data_coding,
                registered_delivery=registered_delivery,
                **submit_kwargs,
            )
            try:
                message_ids.append(await self._send_submit(submit_pdu, timeout))
            except Exception as e:
                e.sent_message_ids = message_ids  # type: ignore[attr-defined]
                raise

        return message_ids

    async def data_sm(
        self,
        source_addr: str,
        destination_addr: str,
        message: str | bytes | bytearray | memoryview,
        source_addr_ton: int = TonType.UNKNOWN,
        source_addr_npi: int = NpiType.UNKNOWN,
        dest_addr_ton: int = TonType.UNKNOWN,
        dest_addr_npi: int = NpiType.UNKNOWN,
        service_type: str = '',
        esm_class: int = 0,
        registered_delivery: int = RegisteredDelivery.NO_RECEIPT,
        data_coding: int = DataCoding.DEFAULT,
        timeout: Optional[float] = None,
    ) -> str:
        """
        Send a message as data_sm, carried in the message_payload TLV

        Unlike submit_sm there is no 254-octet limit and no splitting; the whole
        PDU must fit in 65,536 bytes (a payload of about 65,500 octets).

        Args:
            source_addr: Source address (sender)
            destination_addr: Destination address (recipient)
            message: Text (encoded per data_coding) or raw payload bytes
            source_addr_ton: Source address Type of Number
            source_addr_npi: Source address Numbering Plan Indicator
            dest_addr_ton: Destination address Type of Number
            dest_addr_npi: Destination address Numbering Plan Indicator
            service_type: Service type
            esm_class: ESM class
            registered_delivery: Registered delivery flag
            data_coding: Data coding scheme
            timeout: Response timeout

        Returns:
            Message ID assigned by SMSC

        Raises:
            SMPPInvalidStateException: If not bound as transmitter or transceiver
            SMPPMessageException: If the text can't be encoded or submission fails
        """
        self._require_tx_bind()

        pdu = DataSm(  # type: ignore[call-arg]
            service_type=service_type,
            source_addr_ton=source_addr_ton,
            source_addr_npi=source_addr_npi,
            source_addr=source_addr,
            dest_addr_ton=dest_addr_ton,
            dest_addr_npi=dest_addr_npi,
            destination_addr=destination_addr,
            esm_class=esm_class,
            registered_delivery=registered_delivery,
            data_coding=data_coding,
        )
        try:
            if isinstance(message, (bytes, bytearray, memoryview)):
                pdu.set_message_payload(bytes(message))
            else:
                pdu.set_message_text(message)
            pdu.encode()  # over-size PDU fails here, before a sequence number is used
        except UnicodeEncodeError as e:
            raise SMPPMessageException(
                f'Message not encodable with data_coding {data_coding:#x}; use DataCoding.UCS2'
            ) from e
        except SMPPPDUException as e:
            raise SMPPMessageException(str(e)) from e

        return await self._send_submit(pdu, timeout)

    async def query_sm(
        self,
        message_id: str,
        source_addr: str = '',
        source_addr_ton: int = TonType.UNKNOWN,
        source_addr_npi: int = NpiType.UNKNOWN,
        timeout: Optional[float] = None,
    ) -> QuerySmResp:
        """
        Query the status of a previously submitted message

        Args:
            message_id: SMSC-assigned message ID to query
            source_addr: Source address used on the original submission
            source_addr_ton: Source address Type of Number
            source_addr_npi: Source address Numbering Plan Indicator
            timeout: Response timeout

        Returns:
            QuerySmResp, with typed message_state, final_date and error_code

        Raises:
            SMPPInvalidStateException: If not bound as transmitter or transceiver
            SMPPMessageException: If the query fails
        """
        self._require_tx_bind()

        query_pdu = QuerySm(  # type: ignore[call-arg]
            message_id=message_id,
            source_addr_ton=source_addr_ton,
            source_addr_npi=source_addr_npi,
            source_addr=source_addr,
        )
        response = await self._send_management(query_pdu, timeout)
        return response  # type: ignore[return-value]

    async def cancel_sm(
        self,
        message_id: str,
        source_addr: str = '',
        destination_addr: str = '',
        service_type: str = '',
        source_addr_ton: int = TonType.UNKNOWN,
        source_addr_npi: int = NpiType.UNKNOWN,
        dest_addr_ton: int = TonType.UNKNOWN,
        dest_addr_npi: int = NpiType.UNKNOWN,
        timeout: Optional[float] = None,
    ) -> None:
        """
        Cancel a previously submitted message

        Args:
            message_id: SMSC-assigned message ID to cancel
            source_addr: Source address used on the original submission
            destination_addr: Destination address used on the original submission
            service_type: Service type used on the original submission
            source_addr_ton: Source address Type of Number
            source_addr_npi: Source address Numbering Plan Indicator
            dest_addr_ton: Destination address Type of Number
            dest_addr_npi: Destination address Numbering Plan Indicator
            timeout: Response timeout

        Raises:
            SMPPInvalidStateException: If not bound as transmitter or transceiver
            SMPPMessageException: If the cancel fails
        """
        self._require_tx_bind()

        cancel_pdu = CancelSm(  # type: ignore[call-arg]
            service_type=service_type,
            message_id=message_id,
            source_addr_ton=source_addr_ton,
            source_addr_npi=source_addr_npi,
            source_addr=source_addr,
            dest_addr_ton=dest_addr_ton,
            dest_addr_npi=dest_addr_npi,
            destination_addr=destination_addr,
        )
        await self._send_management(cancel_pdu, timeout)

    async def replace_sm(
        self,
        message_id: str,
        short_message: str,
        source_addr: str = '',
        source_addr_ton: int = TonType.UNKNOWN,
        source_addr_npi: int = NpiType.UNKNOWN,
        data_coding: int = DataCoding.DEFAULT,
        schedule_delivery_time: str = '',
        validity_period: str = '',
        registered_delivery: int = RegisteredDelivery.NO_RECEIPT,
        sm_default_msg_id: int = 0,
        timeout: Optional[float] = None,
    ) -> None:
        """
        Replace the text of a previously submitted message

        replace_sm has no data_coding field of its own; the SMSC applies the
        original message's, so data_coding must match what the message was
        originally submitted with.

        Args:
            message_id: SMSC-assigned message ID to replace
            short_message: New message text
            source_addr: Source address used on the original submission
            source_addr_ton: Source address Type of Number
            source_addr_npi: Source address Numbering Plan Indicator
            data_coding: Data coding used to encode short_message (must match
                the original submission)
            schedule_delivery_time: New scheduled delivery time
            validity_period: New validity period
            registered_delivery: New registered delivery flag
            sm_default_msg_id: New default message ID
            timeout: Response timeout

        Raises:
            SMPPInvalidStateException: If not bound as transmitter or transceiver
            SMPPMessageException: If the message can't be encoded, is too
                long, or the replace fails
        """
        self._require_tx_bind()

        try:
            encoded_message = encode_message_with_encoding(short_message, data_coding)
        except SMPPPDUException as e:
            raise SMPPMessageException(str(e)) from e
        if len(encoded_message) > MAX_SHORT_MESSAGE_LENGTH:
            raise SMPPMessageException(
                f'Message too long: {len(encoded_message)} bytes'
            )

        replace_pdu = ReplaceSm(  # type: ignore[call-arg]
            message_id=message_id,
            source_addr_ton=source_addr_ton,
            source_addr_npi=source_addr_npi,
            source_addr=source_addr,
            schedule_delivery_time=schedule_delivery_time,
            validity_period=validity_period,
            registered_delivery=registered_delivery,
            sm_default_msg_id=sm_default_msg_id,
            short_message=encoded_message,
        )
        await self._send_management(replace_pdu, timeout)

    async def _send_management(self, pdu: PDU, timeout: Optional[float]) -> PDU:
        """Send a query/cancel/replace_sm PDU and raise on a non-ESME_ROK response."""
        try:
            if self._connection is None:
                raise SMPPMessageException('Not connected to SMSC')

            response = await self._connection.send_pdu(
                pdu, wait_response=True, timeout=timeout or self.response_timeout
            )

            if response is None:
                raise SMPPMessageException('No response received from SMSC')

            if response.command_status != CommandStatus.ESME_ROK:
                error_msg = get_error_message(response.command_status)
                exc_type = (
                    SMPPThrottlingException
                    if response.command_status in _THROTTLE_STATUSES
                    else SMPPMessageException
                )
                raise exc_type(
                    error_msg, command_status=response.command_status, pdu=response
                )

            return response

        except SMPPTimeoutException:
            raise SMPPMessageException('Operation timed out')
        except Exception as e:
            if isinstance(e, SMPPMessageException):
                raise
            raise SMPPMessageException(f'Operation failed: {e}')

    async def enquire_link(self, timeout: Optional[float] = None) -> bool:
        """
        Send enquire_link to test connection

        Args:
            timeout: Response timeout

        Returns:
            True if enquire_link successful, False otherwise
        """
        if not self.is_connected:
            raise SMPPInvalidStateException('Not connected to SMSC')

        try:
            enquire_pdu = EnquireLink()

            if self._connection is None:
                return False

            response = await self._connection.send_pdu(
                enquire_pdu,
                wait_response=True,
                timeout=timeout or self.response_timeout,
            )

            return (
                response is not None
                and response.command_status == CommandStatus.ESME_ROK
            )

        except Exception as e:
            logger.error(f'Enquire_link failed: {e}')
            return False

    def _handle_pdu_received(self, pdu: PDU) -> None:
        """Handle received PDU from connection"""
        try:
            if isinstance(pdu, DeliverSm):
                self._handle_deliver_sm(pdu)
            elif isinstance(pdu, DataSm):
                self._handle_data_sm(pdu)
            elif pdu.command_id == CommandId.ENQUIRE_LINK:
                # Respond to enquire_link automatically
                asyncio.create_task(self._send_enquire_link_resp(pdu.sequence_number))
            elif pdu.command_id == CommandId.UNBIND:
                # Handle unbind request from SMSC
                asyncio.create_task(self._handle_unbind_request(pdu.sequence_number))
            else:
                logger.debug('Received unhandled PDU: %s', pdu.__class__.__name__)

        except Exception as e:
            logger.exception(f'Error handling received PDU: {e}')

    def _handle_deliver_sm(self, pdu: DeliverSm) -> None:
        """Handle deliver_sm PDU"""
        logger.debug(
            'Received deliver_sm from %s to %s', pdu.source_addr, pdu.destination_addr
        )

        # Send deliver_sm_resp automatically
        asyncio.create_task(self._send_deliver_sm_resp(pdu.sequence_number))

        # Trigger deliver_sm event
        if self.on_deliver_sm:
            try:
                self.on_deliver_sm(self, pdu)
            except Exception as e:
                logger.exception(f'Error in deliver_sm handler: {e}')

    def _handle_data_sm(self, pdu: DataSm) -> None:
        """Handle an SMSC-initiated data_sm: acknowledge (or refuse if unhandled), then notify"""
        logger.debug(
            'Received data_sm from %s to %s', pdu.source_addr, pdu.destination_addr
        )

        status = (
            CommandStatus.ESME_ROK if self.on_data_sm else CommandStatus.ESME_RX_R_APPN
        )
        asyncio.create_task(self._send_data_sm_resp(pdu.sequence_number, status))

        if self.on_data_sm:
            try:
                self.on_data_sm(self, pdu)
            except Exception as e:
                logger.exception(f'Error in data_sm handler: {e}')

    async def _send_data_sm_resp(
        self, sequence_number: int, status: int = CommandStatus.ESME_ROK
    ) -> None:
        """Send data_sm_resp"""
        try:
            resp_pdu = DataSmResp(
                sequence_number=sequence_number, command_status=status
            )
            if self._connection is not None:
                await self._connection.send_pdu(resp_pdu, wait_response=False)
        except Exception as e:
            logger.error(f'Failed to send data_sm_resp: {e}')

    async def _send_deliver_sm_resp(self, sequence_number: int) -> None:
        """Send deliver_sm_resp"""
        try:
            resp_pdu = DeliverSmResp(sequence_number=sequence_number)
            if self._connection is not None:
                await self._connection.send_pdu(resp_pdu, wait_response=False)
        except Exception as e:
            logger.error(f'Failed to send deliver_sm_resp: {e}')

    async def _send_enquire_link_resp(self, sequence_number: int) -> None:
        """Send enquire_link_resp"""
        try:
            resp_pdu = EnquireLinkResp(sequence_number=sequence_number)
            if self._connection is not None:
                await self._connection.send_pdu(resp_pdu, wait_response=False)
        except Exception as e:
            logger.error(f'Failed to send enquire_link_resp: {e}')

    async def _handle_unbind_request(self, sequence_number: int) -> None:
        """Handle unbind request from SMSC"""
        try:
            resp_pdu = UnbindResp(sequence_number=sequence_number)
            if self._connection is not None:
                await self._connection.send_pdu(resp_pdu, wait_response=False)

            # Update state
            self._bound = False
            self._bind_type = None
            self.sc_interface_version = None

            logger.info('Received unbind request from SMSC')

            # Trigger unbind event
            if self.on_unbind:
                try:
                    self.on_unbind(self)
                except Exception as e:
                    logger.exception(f'Error in unbind handler: {e}')

        except Exception as e:
            logger.error(f'Failed to handle unbind request: {e}')

    def _handle_connection_lost(self, error: Exception) -> None:
        """Handle connection lost event"""
        logger.error(f'Connection lost: {error}')

        self._bound = False
        self._bind_type = None
        self.sc_interface_version = None

        if self.on_connection_lost:
            try:
                self.on_connection_lost(self, error)
            except Exception as e:
                logger.exception(f'Error in connection lost handler: {e}')

    async def __aenter__(self) -> 'SMPPClient':
        """Async context manager entry - automatically connect."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit - automatically disconnect."""
        await self.disconnect()

    async def wait_for_connection(self, timeout: Optional[float] = None) -> bool:
        """
        Wait for connection to be established.

        Args:
            timeout: Maximum time to wait in seconds

        Returns:
            True if connected, False if timeout
        """
        start_time = time.time()
        while not self.is_connected:
            if timeout and (time.time() - start_time) > timeout:
                return False
            await asyncio.sleep(0.1)
        return True

    async def wait_for_bind(self, timeout: Optional[float] = None) -> bool:
        """
        Wait for binding to be completed.

        Args:
            timeout: Maximum time to wait in seconds

        Returns:
            True if bound, False if timeout
        """
        start_time = time.time()
        while not self.is_bound:
            if timeout and (time.time() - start_time) > timeout:
                return False
            await asyncio.sleep(0.1)
        return True

    def __repr__(self) -> str:
        return (
            f'SMPPClient(host={self.host}, port={self.port}, '
            f'system_id={self.system_id}, bound={self.is_bound})'
        )
