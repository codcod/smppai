"""
GSM-specific functionality for SMPP implementation.

This module provides GSM 7-bit encoding, message segmentation,
and concatenated SMS support for compatibility with python-smpplib.
"""

from .constants import (
    SEVENBIT_LENGTH,
    EIGHTBIT_LENGTH,
    UCS2_LENGTH,
    MULTIPART_HEADER_SIZE,
    SEVENBIT_PART_SIZE,
    EIGHTBIT_PART_SIZE,
    UCS2_PART_SIZE,
    SMPP_ENCODING_DEFAULT,
    SMPP_ENCODING_IA5,
    SMPP_ENCODING_BINARY,
    SMPP_ENCODING_ISO88591,
    SMPP_ENCODING_BINARY2,
    SMPP_ENCODING_JIS,
    SMPP_ENCODING_ISO88595,
    SMPP_ENCODING_ISO88598,
    SMPP_ENCODING_ISO10646,
    SMPP_ENCODING_PICTOGRAM,
    SMPP_ENCODING_ISO2022JP,
    SMPP_ENCODING_EXTJIS,
    SMPP_ENCODING_KSC5601,
    SMPP_GSMFEAT_NONE,
    SMPP_GSMFEAT_UDHI,
    SMPP_GSMFEAT_REPLYPATH,
    SMPP_GSMFEAT_UDHIREPLYPATH,
    SMPP_MSGMODE_DEFAULT,
    SMPP_MSGMODE_DATAGRAM,
    SMPP_MSGMODE_FORWARD,
    SMPP_MSGMODE_STOREFORWARD,
    SMPP_MSGTYPE_DEFAULT,
    SMPP_MSGTYPE_DELIVERYACK,
    SMPP_MSGTYPE_USERACK,
)
from .encoding import encode_gsm7, decode_gsm7, encode_gsm0338, decode_gsm0338
from .segmentation import make_parts, MessagePart
from .udh import UDH, UDHElement, ConcatenatedSMSHeader

__all__ = [
    # Encoding functions
    'encode_gsm7',
    'decode_gsm7',
    'encode_gsm0338',
    'decode_gsm0338',
    # Segmentation
    'make_parts',
    'MessagePart',
    # UDH handling
    'UDH',
    'UDHElement',
    'ConcatenatedSMSHeader',
    # Constants (from constants module)
    'SEVENBIT_LENGTH',
    'EIGHTBIT_LENGTH',
    'UCS2_LENGTH',
    'MULTIPART_HEADER_SIZE',
    'SEVENBIT_PART_SIZE',
    'EIGHTBIT_PART_SIZE',
    'UCS2_PART_SIZE',
    'SMPP_ENCODING_DEFAULT',
    'SMPP_ENCODING_IA5',
    'SMPP_ENCODING_BINARY',
    'SMPP_ENCODING_ISO88591',
    'SMPP_ENCODING_BINARY2',
    'SMPP_ENCODING_JIS',
    'SMPP_ENCODING_ISO88595',
    'SMPP_ENCODING_ISO88598',
    'SMPP_ENCODING_ISO10646',
    'SMPP_ENCODING_PICTOGRAM',
    'SMPP_ENCODING_ISO2022JP',
    'SMPP_ENCODING_EXTJIS',
    'SMPP_ENCODING_KSC5601',
    'SMPP_GSMFEAT_NONE',
    'SMPP_GSMFEAT_UDHI',
    'SMPP_GSMFEAT_REPLYPATH',
    'SMPP_GSMFEAT_UDHIREPLYPATH',
    'SMPP_MSGMODE_DEFAULT',
    'SMPP_MSGMODE_DATAGRAM',
    'SMPP_MSGMODE_FORWARD',
    'SMPP_MSGMODE_STOREFORWARD',
    'SMPP_MSGTYPE_DEFAULT',
    'SMPP_MSGTYPE_DELIVERYACK',
    'SMPP_MSGTYPE_USERACK',
]
