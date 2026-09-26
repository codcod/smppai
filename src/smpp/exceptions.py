"""
SMPP Exception Classes

This module defines all SMPP-specific exception classes used throughout the library.
"""

from enum import IntEnum
import typing as tp


class SMPPErrorCode(IntEnum):
    """SMPP-specific error codes for better error categorization."""

    UNKNOWN = 0
    CONNECTION_FAILED = 1000
    BIND_FAILED = 1001
    INVALID_PDU = 1002
    TIMEOUT = 1003
    PROTOCOL_ERROR = 1004
    VALIDATION_ERROR = 1005
    AUTHENTICATION_FAILED = 1006
    THROTTLING = 1007
    MESSAGE_ERROR = 1008
    INVALID_STATE = 1009
    CONFIGURATION_ERROR = 1010
    INVALID_PARAMETER = 1011


class SMPPException(Exception):
    """Base exception for all SMPP-related errors."""

    def __init__(
        self,
        message: str,
        command_status: tp.Optional[int] = None,
        pdu: tp.Optional[tp.Any] = None,
        error_code: tp.Optional[tp.Union[str, SMPPErrorCode]] = None,
        context: tp.Optional[tp.Dict[str, tp.Any]] = None,
        original_error: tp.Optional[Exception] = None,
        **kwargs,
    ):
        super().__init__(message)
        self.command_status = command_status
        self.pdu = pdu
        self.error_code = error_code
        self.context = context or {}
        self.original_error = original_error
        self.details = kwargs

    def __str__(self) -> str:
        """Enhanced string representation with context."""
        parts = [super().__str__()]

        if self.error_code:
            if isinstance(self.error_code, SMPPErrorCode):
                parts.append(
                    f'Error Code: {self.error_code.name} ({self.error_code.value})'
                )
            else:
                parts.append(f'Error Code: {self.error_code}')

        if self.command_status is not None:
            parts.append(f'Command Status: 0x{self.command_status:08X}')

        if self.context:
            context_str = ', '.join(f'{k}={v}' for k, v in self.context.items())
            parts.append(f'Context: {context_str}')

        return ' | '.join(parts)


class SMPPConnectionException(SMPPException):
    """Exception raised for connection-related errors."""

    def __init__(
        self,
        message: str,
        host: tp.Optional[str] = None,
        port: tp.Optional[int] = None,
        connection_state: tp.Optional[str] = None,
        original_error: tp.Optional[Exception] = None,
        **kwargs,
    ):
        context = {}
        if host:
            context['host'] = host
        if port:
            context['port'] = str(port)
        if connection_state:
            context['state'] = connection_state

        super().__init__(
            message,
            error_code=SMPPErrorCode.CONNECTION_FAILED,
            context=context,
            original_error=original_error,
            **kwargs,
        )
        self.host = host
        self.port = port
        self.connection_state = connection_state


class SMPPPDUException(SMPPException):
    """Exception raised for PDU-related errors."""

    def __init__(
        self,
        message: str,
        pdu_type: tp.Optional[str] = None,
        command_id: tp.Optional[int] = None,
        sequence_number: tp.Optional[int] = None,
        original_error: tp.Optional[Exception] = None,
        **kwargs,
    ):
        context = {}
        if pdu_type:
            context['pdu_type'] = pdu_type
        if command_id is not None:
            context['command_id'] = f'0x{command_id:08X}'
        if sequence_number is not None:
            context['sequence_number'] = str(sequence_number)

        # Set default error_code if not provided in kwargs
        if 'error_code' not in kwargs:
            kwargs['error_code'] = SMPPErrorCode.INVALID_PDU

        super().__init__(
            message,
            context=context,
            original_error=original_error,
            **kwargs,
        )
        self.pdu_type = pdu_type
        self.command_id = command_id
        self.sequence_number = sequence_number


class SMPPTimeoutException(SMPPException):
    """Exception raised when operations timeout."""

    def __init__(
        self,
        message: str,
        timeout_duration: tp.Optional[float] = None,
        operation: tp.Optional[str] = None,
        original_error: tp.Optional[Exception] = None,
        **kwargs,
    ):
        context = {}
        if timeout_duration is not None:
            context['timeout_duration'] = str(timeout_duration)
        if operation:
            context['operation'] = operation

        super().__init__(
            message,
            error_code=SMPPErrorCode.TIMEOUT,
            context=context,
            original_error=original_error,
            **kwargs,
        )
        self.timeout_duration = timeout_duration
        self.operation = operation


class SMPPBindException(SMPPException):
    """Exception raised for bind-related errors."""

    def __init__(
        self,
        message: str,
        bind_type: tp.Optional[str] = None,
        system_id: tp.Optional[str] = None,
        original_error: tp.Optional[Exception] = None,
        **kwargs,
    ):
        context = {}
        if bind_type:
            context['bind_type'] = bind_type
        if system_id:
            context['system_id'] = system_id

        super().__init__(
            message,
            error_code=SMPPErrorCode.BIND_FAILED,
            context=context,
            original_error=original_error,
            **kwargs,
        )
        self.bind_type = bind_type
        self.system_id = system_id


class SMPPProtocolException(SMPPException):
    """Exception raised for protocol violations."""

    def __init__(
        self,
        message: str,
        protocol_version: tp.Optional[str] = None,
        original_error: tp.Optional[Exception] = None,
        **kwargs,
    ):
        context = {}
        if protocol_version:
            context['protocol_version'] = protocol_version

        super().__init__(
            message,
            error_code=SMPPErrorCode.PROTOCOL_ERROR,
            context=context,
            original_error=original_error,
            **kwargs,
        )
        self.protocol_version = protocol_version


class SMPPAuthenticationException(SMPPException):
    """Exception raised for authentication failures."""

    def __init__(
        self,
        message: str,
        system_id: tp.Optional[str] = None,
        auth_method: tp.Optional[str] = None,
        original_error: tp.Optional[Exception] = None,
        **kwargs,
    ):
        context = {}
        if system_id:
            context['system_id'] = system_id
        if auth_method:
            context['auth_method'] = auth_method

        super().__init__(
            message,
            error_code=SMPPErrorCode.AUTHENTICATION_FAILED,
            context=context,
            original_error=original_error,
            **kwargs,
        )
        self.system_id = system_id
        self.auth_method = auth_method


class SMPPInvalidStateException(SMPPException):
    """Exception raised when operation is attempted in invalid state."""

    def __init__(
        self,
        message: str,
        current_state: tp.Optional[str] = None,
        expected_state: tp.Optional[str] = None,
        operation: tp.Optional[str] = None,
        original_error: tp.Optional[Exception] = None,
        **kwargs,
    ):
        context = {}
        if current_state:
            context['current_state'] = current_state
        if expected_state:
            context['expected_state'] = expected_state
        if operation:
            context['operation'] = operation

        super().__init__(
            message,
            error_code=SMPPErrorCode.INVALID_STATE,
            context=context,
            original_error=original_error,
            **kwargs,
        )
        self.current_state = current_state
        self.expected_state = expected_state
        self.operation = operation


class SMPPMessageException(SMPPException):
    """Exception raised for message-related errors."""

    def __init__(
        self,
        message: str,
        message_id: tp.Optional[str] = None,
        destination: tp.Optional[str] = None,
        original_error: tp.Optional[Exception] = None,
        **kwargs,
    ):
        context = {}
        if message_id:
            context['message_id'] = message_id
        if destination:
            context['destination'] = destination

        super().__init__(
            message,
            error_code=SMPPErrorCode.MESSAGE_ERROR,
            context=context,
            original_error=original_error,
            **kwargs,
        )
        self.message_id = message_id
        self.destination = destination


class SMPPThrottlingException(SMPPMessageException):
    """Exception raised when the SMSC asks the client to slow down.

    Raised by ``submit_sm`` on ESME_RTHROTTLED / ESME_RMSGQFUL. Subclasses
    SMPPMessageException so existing message-error handlers still catch it.
    """

    def __init__(
        self,
        message: str,
        current_rate: tp.Optional[float] = None,
        max_rate: tp.Optional[float] = None,
        original_error: tp.Optional[Exception] = None,
        **kwargs,
    ):
        # SMPPMessageException passes error_code/context to its parent itself,
        # so set them after super() rather than forwarding them.
        super().__init__(message, original_error=original_error, **kwargs)
        self.error_code = SMPPErrorCode.THROTTLING
        if current_rate is not None:
            self.context['current_rate'] = current_rate
        if max_rate is not None:
            self.context['max_rate'] = max_rate
        self.current_rate = current_rate
        self.max_rate = max_rate


class SMPPValidationException(SMPPException):
    """Exception raised for validation errors."""

    def __init__(
        self,
        message: str,
        field_name: tp.Optional[str] = None,
        field_value: tp.Optional[str] = None,
        validation_rule: tp.Optional[str] = None,
        original_error: tp.Optional[Exception] = None,
        **kwargs,
    ):
        context = {}
        if field_name:
            context['field_name'] = field_name
        if field_value:
            context['field_value'] = field_value
        if validation_rule:
            context['validation_rule'] = validation_rule

        super().__init__(
            message,
            error_code=SMPPErrorCode.VALIDATION_ERROR,
            context=context,
            original_error=original_error,
            **kwargs,
        )
        self.field_name = field_name
        self.field_value = field_value
        self.validation_rule = validation_rule


class SMPPConfigurationException(SMPPException):
    """Exception raised for configuration-related errors."""

    def __init__(
        self,
        message: str,
        config_section: tp.Optional[str] = None,
        config_key: tp.Optional[str] = None,
        config_value: tp.Optional[str] = None,
        original_error: tp.Optional[Exception] = None,
        **kwargs,
    ):
        context = {}
        if config_section:
            context['config_section'] = config_section
        if config_key:
            context['config_key'] = config_key
        if config_value:
            context['config_value'] = config_value

        super().__init__(
            message,
            error_code=SMPPErrorCode.CONFIGURATION_ERROR,
            context=context,
            original_error=original_error,
            **kwargs,
        )
        self.config_section = config_section
        self.config_key = config_key
        self.config_value = config_value
