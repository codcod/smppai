"""
GSM constants for compatibility with python-smpplib.

Provides constants for message lengths, encoding types, and other GSM-specific values.
"""

# Message part lengths in different encodings (compatible with python-smpplib)
SEVENBIT_LENGTH = 160
EIGHTBIT_LENGTH = 140
UCS2_LENGTH = 140

MULTIPART_HEADER_SIZE = 6

SEVENBIT_PART_SIZE = SEVENBIT_LENGTH - 7  # Reserve space for UDH
EIGHTBIT_PART_SIZE = EIGHTBIT_LENGTH - MULTIPART_HEADER_SIZE
UCS2_PART_SIZE = UCS2_LENGTH - MULTIPART_HEADER_SIZE

# Encoding types (compatible with python-smpplib)
SMPP_ENCODING_DEFAULT = 0x00  # SMSC Default
SMPP_ENCODING_IA5 = 0x01  # IA5 (CCITT T.50)/ASCII (ANSI X3.4)
SMPP_ENCODING_BINARY = 0x02  # Octet unspecified (8-bit binary)
SMPP_ENCODING_ISO88591 = 0x03  # Latin 1 (ISO-8859-1)
SMPP_ENCODING_BINARY2 = 0x04  # Octet unspecified (8-bit binary)
SMPP_ENCODING_JIS = 0x05  # JIS (X 0208-1990)
SMPP_ENCODING_ISO88595 = 0x06  # Cyrillic (ISO-8859-5)
SMPP_ENCODING_ISO88598 = 0x07  # Latin/Hebrew (ISO-8859-8)
SMPP_ENCODING_ISO10646 = 0x08  # UCS2 (ISO/IEC-10646)
SMPP_ENCODING_PICTOGRAM = 0x09  # Pictogram Encoding
SMPP_ENCODING_ISO2022JP = 0x0A  # ISO-2022-JP (Music Codes)
SMPP_ENCODING_EXTJIS = 0x0D  # Extended Kanji JIS (X 0212-1990)
SMPP_ENCODING_KSC5601 = 0x0E  # KS C 5601

# GSM Feature flags
SMPP_GSMFEAT_NONE = 0x00  # No specific features selected
SMPP_GSMFEAT_UDHI = 0x40  # UDHI Indicator (only relevant for MT msgs)
SMPP_GSMFEAT_REPLYPATH = 0x80  # Set Reply Path (only relevant for GSM net)
SMPP_GSMFEAT_UDHIREPLYPATH = 0xC0  # Set UDHI and Reply Path (for GSM net)

# Message mode flags
SMPP_MSGMODE_DEFAULT = 0x00  # Default SMSC mode (e.g. Store and Forward)
SMPP_MSGMODE_DATAGRAM = 0x01  # Datagram mode
SMPP_MSGMODE_FORWARD = 0x02  # Forward (i.e. Transaction) mode
SMPP_MSGMODE_STOREFORWARD = 0x03  # Explicit Store and Forward mode

# Message type flags
SMPP_MSGTYPE_DEFAULT = 0x00  # Default message type (i.e. normal message)
SMPP_MSGTYPE_DELIVERYACK = 0x08  # Message contains ESME Delivery acknowledgement
SMPP_MSGTYPE_USERACK = 0x10  # Message contains ESME Manual/User acknowledgement
