"""Unit tests for CommandStatus values against SMPP v3.4 Table 5-2."""

from smpp.protocol.constants import ERROR_MESSAGES, CommandStatus


def test_command_status_has_no_aliases():
    # IntEnum silently turns a duplicate value into an alias of the first member.
    assert len(CommandStatus.__members__) == len(list(CommandStatus))


# SMPP v3.4 Table 5-2, transcribed independently of constants.py.
# Library names differ from the spec for 0x0B (ESME_RINVDSTADR) and 0x61 (ESME_RINVSCHED).
SPEC_TABLE_5_2 = {
    'ESME_ROK': 0x00,
    'ESME_RINVMSGLEN': 0x01,
    'ESME_RINVCMDLEN': 0x02,
    'ESME_RINVCMDID': 0x03,
    'ESME_RINVBNDSTS': 0x04,
    'ESME_RALYBND': 0x05,
    'ESME_RINVPRTFLG': 0x06,
    'ESME_RINVREGDLVFLG': 0x07,
    'ESME_RSYSERR': 0x08,
    'ESME_RINVSRCADR': 0x0A,
    'ESME_RINVDESTADR': 0x0B,
    'ESME_RINVMSGID': 0x0C,
    'ESME_RBINDFAIL': 0x0D,
    'ESME_RINVPASWD': 0x0E,
    'ESME_RINVSYSID': 0x0F,
    'ESME_RCANCELFAIL': 0x11,
    'ESME_RREPLACEFAIL': 0x13,
    'ESME_RMSGQFUL': 0x14,
    'ESME_RINVSERTYP': 0x15,
    'ESME_RINVNUMDESTS': 0x33,
    'ESME_RINVDLNAME': 0x34,
    'ESME_RINVDESTFLAG': 0x40,
    'ESME_RINVSUBREP': 0x42,
    'ESME_RINVESMCLASS': 0x43,
    'ESME_RCNTSUBDL': 0x44,
    'ESME_RSUBMITFAIL': 0x45,
    'ESME_RINVSRCTON': 0x48,
    'ESME_RINVSRCNPI': 0x49,
    'ESME_RINVDSTTON': 0x50,
    'ESME_RINVDSTNPI': 0x51,
    'ESME_RINVSYSTYP': 0x53,
    'ESME_RINVREPFLAG': 0x54,
    'ESME_RINVNUMMSGS': 0x55,
    'ESME_RTHROTTLED': 0x58,
    'ESME_RINVPTIME': 0x61,
    'ESME_RINVEXPIRY': 0x62,
    'ESME_RINVDFTMSGID': 0x63,
    'ESME_RX_T_APPN': 0x64,
    'ESME_RX_P_APPN': 0x65,
    'ESME_RX_R_APPN': 0x66,
    'ESME_RQUERYFAIL': 0x67,
    'ESME_RINVOPTPARSTREAM': 0xC0,
    'ESME_ROPTPARNOTALLWD': 0xC1,
    'ESME_RINVPARLEN': 0xC2,
    'ESME_RMISSINGOPTPARAM': 0xC3,
    'ESME_RINVOPTPARAMVAL': 0xC4,
    'ESME_RDELIVERYFAILURE': 0xFE,
    'ESME_RUNKNOWNERR': 0xFF,
}


def test_command_status_matches_spec_table():
    assert {s.name: s.value for s in CommandStatus} == SPEC_TABLE_5_2


def test_every_command_status_has_error_message():
    assert all(status in ERROR_MESSAGES for status in CommandStatus)
