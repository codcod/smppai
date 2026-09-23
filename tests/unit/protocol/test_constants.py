"""Unit tests for CommandStatus values against SMPP v3.4 Table 5-2."""

import pytest
from smpp.protocol.constants import ERROR_MESSAGES, CommandStatus


def test_command_status_has_no_aliases():
    # IntEnum silently turns a duplicate value into an alias of the first member.
    assert len(CommandStatus.__members__) == len(list(CommandStatus))


@pytest.mark.parametrize(
    'status, value',
    [
        (CommandStatus.ESME_RINVPASWD, 0x0E),
        (CommandStatus.ESME_RSYSERR, 0x08),
        (CommandStatus.ESME_RMSGQFUL, 0x14),
        (CommandStatus.ESME_RSUBMITFAIL, 0x45),
        (CommandStatus.ESME_RTHROTTLED, 0x58),
        (CommandStatus.ESME_RQUERYFAIL, 0x67),
    ],
)
def test_command_status_spec_values(status, value):
    assert status == value


def test_every_command_status_has_error_message():
    assert all(status in ERROR_MESSAGES for status in CommandStatus)
