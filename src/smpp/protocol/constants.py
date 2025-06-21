"""
SMPP v3.4 Protocol Constants and Enumerations

This module contains all the constants, command IDs, status codes, and enumerations
defined in the SMPP v3.4 specification.
"""

from enum import IntEnum
from typing import Dict


class CommandId(IntEnum):
    """SMPP Command IDs as defined in SMPP v3.4 specification"""

    # Session Management Operations
    BIND_RECEIVER = 0x00000001
    BIND_RECEIVER_RESP = 0x80000001
    BIND_TRANSMITTER = 0x00000002
    BIND_TRANSMITTER_RESP = 0x80000002
    QUERY_SM = 0x00000003
    QUERY_SM_RESP = 0x80000003
    SUBMIT_SM = 0x00000004
    SUBMIT_SM_RESP = 0x80000004
    DELIVER_SM = 0x00000005
    DELIVER_SM_RESP = 0x80000005
    UNBIND = 0x00000006
    UNBIND_RESP = 0x80000006
    REPLACE_SM = 0x00000007
    REPLACE_SM_RESP = 0x80000007
    CANCEL_SM = 0x00000008
    CANCEL_SM_RESP = 0x80000008
    BIND_TRANSCEIVER = 0x00000009
    BIND_TRANSCEIVER_RESP = 0x80000009
    OUTBIND = 0x0000000B
    ENQUIRE_LINK = 0x00000015
    ENQUIRE_LINK_RESP = 0x80000015
    SUBMIT_MULTI = 0x00000021
    SUBMIT_MULTI_RESP = 0x80000021
    ALERT_NOTIFICATION = 0x00000102
    DATA_SM = 0x00000103
    DATA_SM_RESP = 0x80000103
    GENERIC_NACK = 0x80000000


class CommandStatus(IntEnum):
    """SMPP Command Status codes as defined in SMPP v3.4 specification"""

    ESME_ROK = 0x00000000  # No Error
    ESME_RINVMSGLEN = 0x00000001  # Message Length is invalid
    ESME_RINVCMDLEN = 0x00000002  # Command Length is invalid
    ESME_RINVCMDID = 0x00000003  # Invalid Command ID
    ESME_RINVBNDSTS = 0x00000004  # Incorrect BIND Status for given command
    ESME_RALYBND = 0x00000005  # ESME Already in Bound State
    ESME_RINVPASWD = 0x00000006  # Invalid Password
    ESME_RINVSYSID = 0x00000007  # Invalid System ID
    ESME_RCANCELFAIL = 0x00000008  # Cancel SM Failed
    ESME_RREPLACEFAIL = 0x00000009  # Replace SM Failed
    ESME_RMSGQFUL = 0x0000000A  # Message Queue Full
    ESME_RINVSERTYP = 0x0000000B  # Invalid Service Type
    ESME_RINVNUMDESTS = 0x0000000C  # Invalid number of destinations
    ESME_RINVDLNAME = 0x0000000D  # Invalid Distribution List name
    ESME_RINVDESTFLAG = 0x0000000E  # Destination flag is invalid
    ESME_RINVSUBREP = 0x0000000F  # Invalid 'submit with replace' request
    ESME_RINVESMCLASS = 0x00000010  # Invalid esm_class field data
    ESME_RCNTSUBDL = 0x00000011  # Cannot Submit to Distribution List
    ESME_RSUBMITFAIL = 0x00000012  # submit_sm or submit_multi failed
    ESME_RINVSRCADR = 0x00000013  # Invalid Source address TON
    ESME_RINVDESTADR = 0x00000014  # Invalid Dest Addr TON
    ESME_RINVMSGID = 0x00000015  # Invalid message_id
    ESME_RBINDFAIL = 0x00000016  # Bind Failed
    ESME_RINVPTIME = 0x00000033  # Invalid scheduled delivery time
    ESME_RINVEXPIRY = 0x00000034  # Invalid message validity period
    ESME_RINVDFTMSGID = 0x00000035  # Predefined Message Invalid or Not Found
    ESME_RX_T_APPN = 0x00000036  # ESME Receiver Temporary App Error Code
    ESME_RX_P_APPN = 0x00000037  # ESME Receiver Permanent App Error Code
    ESME_RX_R_APPN = 0x00000038  # ESME Receiver Reject Message Error Code
    ESME_RQUERYFAIL = 0x00000039  # query_sm request failed
    ESME_RINVOPTPARSTREAM = 0x000000C0  # Error in the optional part of the PDU Body
    ESME_ROPTPARNOTALLWD = 0x000000C1  # Optional Parameter not allowed
    ESME_RINVPARLEN = 0x000000C2  # Invalid Parameter Length
    ESME_RMISSINGOPTPARAM = 0x000000C3  # Expected Optional Parameter missing
    ESME_RINVOPTPARAMVAL = 0x000000C4  # Invalid Optional Parameter Value
    ESME_RDELIVERYFAILURE = 0x000000FE  # Delivery Failure (used for data_sm_resp)
    ESME_RUNKNOWNERR = 0x000000FF  # Unknown Error


class TonType(IntEnum):
    """Type of Number (TON) values"""

    UNKNOWN = 0x00
    INTERNATIONAL = 0x01
    NATIONAL = 0x02
    NETWORK_SPECIFIC = 0x03
    SUBSCRIBER = 0x04
    ALPHANUMERIC = 0x05
    ABBREVIATED = 0x06


class NpiType(IntEnum):
    """Numbering Plan Indicator (NPI) values"""

    UNKNOWN = 0x00
    ISDN = 0x01  # ISDN (E163/E164)
    DATA = 0x03  # Data (X.121)
    TELEX = 0x04  # Telex (F.69)
    LAND_MOBILE = 0x06  # Land Mobile (E.212)
    NATIONAL = 0x08
    PRIVATE = 0x09
    ERMES = 0x0A
    INTERNET = 0x0E  # Internet (IP)
    WAP_CLIENT_ID = 0x12  # WAP Client Id (to be defined by WAP Forum)


class DataCoding(IntEnum):
    """Data Coding Scheme values"""

    DEFAULT = 0x00  # SMSC Default Alphabet
    IA5_ASCII = 0x01  # IA5 (CCITT T.50)/ASCII (ANSI X3.4)
    OCTET_UNSPECIFIED_1 = 0x02  # Octet unspecified (8-bit binary)
    LATIN_1 = 0x03  # Latin 1 (ISO-8859-1)
    OCTET_UNSPECIFIED_2 = 0x04  # Octet unspecified (8-bit binary)
    JIS = 0x05  # JIS (X 0208-1990)
    CYRILLIC = 0x06  # Cyrillic (ISO-8859-5)
    LATIN_HEBREW = 0x07  # Latin/Hebrew (ISO-8859-8)
    UCS2 = 0x08  # UCS2 (ISO/IEC-10646)
    PICTOGRAM = 0x09  # Pictogram Encoding
    ISO_2022_JP = 0x0A  # ISO-2022-JP (Music Codes)
    EXTENDED_KANJI_JIS = 0x0D  # Extended Kanji JIS(X 0212-1990)
    KS_C_5601 = 0x0E  # KS C 5601


class EsmClass(IntEnum):
    """ESM Class values - Messaging Mode"""

    DEFAULT = 0x00  # Default SMSC Mode
    DATAGRAM = 0x01  # Datagram mode
    FORWARD = 0x02  # Forward (i.e. Transaction) mode
    STORE_FORWARD = 0x03  # Store and Forward mode


class PriorityFlag(IntEnum):
    """Priority Flag values"""

    LEVEL_0 = 0x00  # Level 0 (lowest) priority
    LEVEL_1 = 0x01  # Level 1 priority
    LEVEL_2 = 0x02  # Level 2 priority
    LEVEL_3 = 0x03  # Level 3 (highest) priority


class RegisteredDelivery(IntEnum):
    """Registered Delivery values"""

    NO_RECEIPT = 0x00  # No SMSC Delivery Receipt requested
    SUCCESS_FAILURE = 0x01  # SMSC Delivery Receipt requested where final delivery outcome is delivery success or failure
    FAILURE_ONLY = 0x02  # SMSC Delivery Receipt requested where the final delivery outcome is delivery failure


class ReplaceIfPresentFlag(IntEnum):
    """Replace If Present Flag values"""

    DONT_REPLACE = 0x00  # Don't replace
    REPLACE = 0x01  # Replace


class InterfaceVersion(IntEnum):
    """Interface Version values"""

    VERSION_3_3 = 0x33  # SMPP Version 3.3
    VERSION_3_4 = 0x34  # SMPP Version 3.4


class MessageState(IntEnum):
    """Message State values for delivery receipts"""

    ENROUTE = 0x01  # The message is in enroute state
    DELIVERED = 0x02  # Message is delivered to destination
    EXPIRED = 0x03  # Message expired before delivery
    DELETED = 0x04  # Message has been deleted
    UNDELIVERABLE = 0x05  # Message is undeliverable
    ACCEPTED = 0x06  # Message is in accepted state
    UNKNOWN = 0x07  # Message is invalid state
    REJECTED = 0x08  # Message is in a rejected state


# Optional Parameter Tags (TLV Tags)
class OptionalTag(IntEnum):
    """Optional Parameter Tags for TLV (Tag-Length-Value) parameters"""

    DEST_ADDR_SUBUNIT = 0x0005
    DEST_NETWORK_TYPE = 0x0006
    DEST_BEARER_TYPE = 0x0007
    DEST_TELEMATICS_ID = 0x0008
    SOURCE_ADDR_SUBUNIT = 0x000D
    SOURCE_NETWORK_TYPE = 0x000E
    SOURCE_BEARER_TYPE = 0x000F
    SOURCE_TELEMATICS_ID = 0x0010
    QOS_TIME_TO_LIVE = 0x0017
    PAYLOAD_TYPE = 0x0019
    ADDITIONAL_STATUS_INFO_TEXT = 0x001D
    RECEIPTED_MESSAGE_ID = 0x001E
    MS_MSG_WAIT_FACILITIES = 0x0030
    PRIVACY_INDICATOR = 0x0201
    SOURCE_SUBADDRESS = 0x0202
    DEST_SUBADDRESS = 0x0203
    USER_MESSAGE_REFERENCE = 0x0204
    USER_RESPONSE_CODE = 0x0205
    SOURCE_PORT = 0x020A
    DESTINATION_PORT = 0x020B
    SAR_MSG_REF_NUM = 0x020C
    LANGUAGE_INDICATOR = 0x020D
    SAR_TOTAL_SEGMENTS = 0x020E
    SAR_SEGMENT_SEQNUM = 0x020F
    SC_INTERFACE_VERSION = 0x0210
    CALLBACK_NUM_PRES_IND = 0x0302
    CALLBACK_NUM_ATAG = 0x0303
    NUMBER_OF_MESSAGES = 0x0304
    CALLBACK_NUM = 0x0381
    DPF_RESULT = 0x0420
    SET_DPF = 0x0421
    MS_AVAILABILITY_STATUS = 0x0422
    NETWORK_ERROR_CODE = 0x0423
    MESSAGE_PAYLOAD = 0x0424
    DELIVERY_FAILURE_REASON = 0x0425
    MORE_MESSAGES_TO_SEND = 0x0426
    MESSAGE_STATE = 0x0427
    USSD_SERVICE_OP = 0x0501
    DISPLAY_TIME = 0x1201
    SMS_SIGNAL = 0x1203
    MS_VALIDITY = 0x1204
    ALERT_ON_MESSAGE_DELIVERY = 0x130C
    ITS_REPLY_TYPE = 0x1380
    ITS_SESSION_INFO = 0x1383


# Default Values
DEFAULT_SYSTEM_TYPE = ''
DEFAULT_INTERFACE_VERSION = InterfaceVersion.VERSION_3_4
DEFAULT_ADDR_TON = TonType.UNKNOWN
DEFAULT_ADDR_NPI = NpiType.UNKNOWN
DEFAULT_SERVICE_TYPE = ''
DEFAULT_ESM_CLASS = EsmClass.DEFAULT
DEFAULT_PROTOCOL_ID = 0
DEFAULT_PRIORITY_FLAG = PriorityFlag.LEVEL_0
DEFAULT_SCHEDULE_DELIVERY_TIME = ''
DEFAULT_VALIDITY_PERIOD = ''
DEFAULT_REGISTERED_DELIVERY = RegisteredDelivery.NO_RECEIPT
DEFAULT_REPLACE_IF_PRESENT_FLAG = ReplaceIfPresentFlag.DONT_REPLACE
DEFAULT_DATA_CODING = DataCoding.DEFAULT
DEFAULT_SM_DEFAULT_MSG_ID = 0

# PDU Structure Constants
PDU_HEADER_SIZE = 16  # Size of PDU header in bytes
MAX_PDU_SIZE = 65536  # Maximum PDU size
MAX_SHORT_MESSAGE_LENGTH = 255  # Maximum short message length
MAX_SYSTEM_ID_LENGTH = 16
MAX_PASSWORD_LENGTH = 9
MAX_SYSTEM_TYPE_LENGTH = 13
MAX_ADDRESS_RANGE_LENGTH = 41
MAX_ADDRESS_LENGTH = 21
MAX_SERVICE_TYPE_LENGTH = 6

# Error Messages
ERROR_MESSAGES: Dict[int, str] = {
    CommandStatus.ESME_ROK: 'No Error',
    CommandStatus.ESME_RINVMSGLEN: 'Message Length is invalid',
    CommandStatus.ESME_RINVCMDLEN: 'Command Length is invalid',
    CommandStatus.ESME_RINVCMDID: 'Invalid Command ID',
    CommandStatus.ESME_RINVBNDSTS: 'Incorrect BIND Status for given command',
    CommandStatus.ESME_RALYBND: 'ESME Already in Bound State',
    CommandStatus.ESME_RINVPASWD: 'Invalid Password',
    CommandStatus.ESME_RINVSYSID: 'Invalid System ID',
    CommandStatus.ESME_RCANCELFAIL: 'Cancel SM Failed',
    CommandStatus.ESME_RREPLACEFAIL: 'Replace SM Failed',
    CommandStatus.ESME_RMSGQFUL: 'Message Queue Full',
    CommandStatus.ESME_RINVSERTYP: 'Invalid Service Type',
    CommandStatus.ESME_RINVNUMDESTS: 'Invalid number of destinations',
    CommandStatus.ESME_RINVDLNAME: 'Invalid Distribution List name',
    CommandStatus.ESME_RINVDESTFLAG: 'Destination flag is invalid',
    CommandStatus.ESME_RINVSUBREP: "Invalid 'submit with replace' request",
    CommandStatus.ESME_RINVESMCLASS: 'Invalid esm_class field data',
    CommandStatus.ESME_RCNTSUBDL: 'Cannot Submit to Distribution List',
    CommandStatus.ESME_RSUBMITFAIL: 'submit_sm or submit_multi failed',
    CommandStatus.ESME_RINVSRCADR: 'Invalid Source address TON',
    CommandStatus.ESME_RINVDESTADR: 'Invalid Dest Addr TON',
    CommandStatus.ESME_RINVMSGID: 'Invalid message_id',
    CommandStatus.ESME_RBINDFAIL: 'Bind Failed',
    CommandStatus.ESME_RINVPTIME: 'Invalid scheduled delivery time',
    CommandStatus.ESME_RINVEXPIRY: 'Invalid message validity period',
    CommandStatus.ESME_RINVDFTMSGID: 'Predefined Message Invalid or Not Found',
    CommandStatus.ESME_RX_T_APPN: 'ESME Receiver Temporary App Error Code',
    CommandStatus.ESME_RX_P_APPN: 'ESME Receiver Permanent App Error Code',
    CommandStatus.ESME_RX_R_APPN: 'ESME Receiver Reject Message Error Code',
    CommandStatus.ESME_RQUERYFAIL: 'query_sm request failed',
    CommandStatus.ESME_RINVOPTPARSTREAM: 'Error in the optional part of the PDU Body',
    CommandStatus.ESME_ROPTPARNOTALLWD: 'Optional Parameter not allowed',
    CommandStatus.ESME_RINVPARLEN: 'Invalid Parameter Length',
    CommandStatus.ESME_RMISSINGOPTPARAM: 'Expected Optional Parameter missing',
    CommandStatus.ESME_RINVOPTPARAMVAL: 'Invalid Optional Parameter Value',
    CommandStatus.ESME_RDELIVERYFAILURE: 'Delivery Failure',
    CommandStatus.ESME_RUNKNOWNERR: 'Unknown Error',
}


def get_error_message(status_code: int) -> str:
    """Get human-readable error message for a status code"""
    return ERROR_MESSAGES.get(status_code, f'Unknown error code: 0x{status_code:08X}')


def is_response_command(command_id: int) -> bool:
    """Check if a command ID represents a response PDU"""
    return bool(command_id & 0x80000000)


def get_response_command_id(command_id: int) -> int:
    """Get the response command ID for a given request command ID"""
    return command_id | 0x80000000


def get_request_command_id(command_id: int) -> int:
    """Get the request command ID for a given response command ID"""
    return command_id & 0x7FFFFFFF
