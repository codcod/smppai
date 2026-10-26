"""Unit tests for the SMPP exception hierarchy."""

import pytest

from smpp.exceptions import (
    SMPPAuthenticationException,
    SMPPBindException,
    SMPPConfigurationException,
    SMPPConnectionException,
    SMPPErrorCode,
    SMPPException,
    SMPPInvalidStateException,
    SMPPMessageException,
    SMPPPDUException,
    SMPPProtocolException,
    SMPPThrottlingException,
    SMPPTimeoutException,
    SMPPValidationException,
)

# (class, every optional context kwarg, expected error code, expected context)
CASES = [
    (
        SMPPConnectionException,
        {'host': 'smsc', 'port': 2775, 'connection_state': 'OPEN'},
        SMPPErrorCode.CONNECTION_FAILED,
        {'host': 'smsc', 'port': '2775', 'state': 'OPEN'},
    ),
    (
        SMPPPDUException,
        {'pdu_type': 'submit_sm', 'command_id': 4, 'sequence_number': 9},
        SMPPErrorCode.INVALID_PDU,
        {'pdu_type': 'submit_sm', 'command_id': '0x00000004', 'sequence_number': '9'},
    ),
    (
        SMPPTimeoutException,
        {'timeout_duration': 1.5, 'operation': 'bind'},
        SMPPErrorCode.TIMEOUT,
        {'timeout_duration': '1.5', 'operation': 'bind'},
    ),
    (
        SMPPBindException,
        {'bind_type': 'transceiver', 'system_id': 'esme'},
        SMPPErrorCode.BIND_FAILED,
        {'bind_type': 'transceiver', 'system_id': 'esme'},
    ),
    (
        SMPPProtocolException,
        {'protocol_version': '3.4'},
        SMPPErrorCode.PROTOCOL_ERROR,
        {'protocol_version': '3.4'},
    ),
    (
        SMPPAuthenticationException,
        {'system_id': 'esme', 'auth_method': 'password'},
        SMPPErrorCode.AUTHENTICATION_FAILED,
        {'system_id': 'esme', 'auth_method': 'password'},
    ),
    (
        SMPPInvalidStateException,
        {'current_state': 'OPEN', 'expected_state': 'BOUND', 'operation': 'submit'},
        SMPPErrorCode.INVALID_STATE,
        {'current_state': 'OPEN', 'expected_state': 'BOUND', 'operation': 'submit'},
    ),
    (
        SMPPMessageException,
        {'message_id': 'm1', 'destination': '123'},
        SMPPErrorCode.MESSAGE_ERROR,
        {'message_id': 'm1', 'destination': '123'},
    ),
    (
        SMPPThrottlingException,
        {'current_rate': 12.0, 'max_rate': 10.0},
        SMPPErrorCode.THROTTLING,
        {'current_rate': 12.0, 'max_rate': 10.0},
    ),
    (
        SMPPValidationException,
        {'field_name': 'addr', 'field_value': 'x', 'validation_rule': 'max_length'},
        SMPPErrorCode.VALIDATION_ERROR,
        {'field_name': 'addr', 'field_value': 'x', 'validation_rule': 'max_length'},
    ),
    (
        SMPPConfigurationException,
        {'config_section': 'client', 'config_key': 'port', 'config_value': 'abc'},
        SMPPErrorCode.CONFIGURATION_ERROR,
        {'config_section': 'client', 'config_key': 'port', 'config_value': 'abc'},
    ),
]


@pytest.mark.parametrize(
    'cls,kwargs,code,context', CASES, ids=[c[0].__name__ for c in CASES]
)
class TestExceptionContext:
    def test_with_context(self, cls, kwargs, code, context):
        err = cls('boom', **kwargs)
        assert isinstance(err, SMPPException)
        assert err.error_code == code
        assert err.context == context
        for name, value in kwargs.items():
            assert getattr(err, name) == value
        assert str(err).startswith(f'boom | Error Code: {code.name} ({code.value})')
        assert 'Context: ' in str(err)

    def test_without_context(self, cls, kwargs, code, context):
        err = cls('boom')
        assert err.error_code == code
        assert err.context == {}
        for name in kwargs:
            assert getattr(err, name) is None
        assert str(err) == f'boom | Error Code: {code.name} ({code.value})'


class TestSMPPException:
    def test_plain_message(self):
        assert str(SMPPException('boom')) == 'boom'

    def test_string_error_code_and_command_status(self):
        err = SMPPException('boom', command_status=0x45, error_code='CUSTOM', extra=1)
        assert str(err) == 'boom | Error Code: CUSTOM | Command Status: 0x00000045'
        assert err.details == {'extra': 1}

    def test_original_error_is_kept(self):
        cause = ValueError('bad')
        assert SMPPBindException('boom', original_error=cause).original_error is cause

    def test_pdu_exception_error_code_override(self):
        err = SMPPPDUException('boom', error_code=SMPPErrorCode.VALIDATION_ERROR)
        assert err.error_code == SMPPErrorCode.VALIDATION_ERROR

    def test_throttling_is_a_message_exception(self):
        assert isinstance(SMPPThrottlingException('slow down'), SMPPMessageException)
