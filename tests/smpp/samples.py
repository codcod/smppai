"""Sample Operations (frames, PDUs) for testing.
"""

import binascii
import struct
from dataclasses import dataclass


@dataclass
class PDUSample:
    """Base class for samples.

    Adds `frame` attribute and `asdict()` method that are used in asserts.
    """

    def __post_init__(self):
        self._setattr_frame()

    def _setattr_frame(self):
        hex = []
        for f in self.__dataclass_fields__:
            hex.append(getattr(self, f))
        hex = b''.join(hex).replace(b' ', b'')
        bin = binascii.a2b_hex(hex)
        setattr(self, 'frame', bin)
        setattr(self, 'length', int2bin(len(bin)))  # overwrite length

    def asdict(self):
        params = {}
        str_fields = ['sys_id', 'password', 'sys_type', 'addr_range']
        for f in self.__dataclass_fields__:
            val = getattr(self, f)
            val = val.replace(b' ', b'')
            if f in str_fields:
                if val == b'00':
                    val = b''
                else:
                    val = binascii.unhexlify(val).replace(b'\x00', b'')
            else:
                val = int.from_bytes(binascii.unhexlify(val), byteorder='big')
            params[f] = val
        return params


def str2bin(s: str, endswith: str = '00') -> bytes:
    r = ''.join([f'{c:X} ' for c in s.encode()]) + endswith
    if endswith == '': r = r.strip()
    return r.encode()


def int2bin(i: int, format: str = '>L') -> bytes:
    return binascii.b2a_hex(struct.pack(format, i)).upper()


@dataclass
class BindTransmitterPDUSample1(PDUSample):
    length: bytes           = b'00 00 00 2F'                    # 47, 0x0000002f                | Integer(4)
    id: bytes               = b'00 00 00 02'                    # "bind_trasmitter", 0x00000002 | Integer(4)
    status: bytes           = b'00 00 00 00'                    # 0            | Integer(4)
    sequence: bytes         = b'00 00 00 01'                    # 1            | Integer(4)
    sys_id: bytes           = b'53 4D 50 50 33 54 45 53 54 00'  # "SMPP3TEST"  | size max 16 C-Octet String)
    password: bytes         = b'73 65 63 72 65 74 30 38 00'     # "secret08"   | max size 9 C-Octet String)
    sys_type: bytes         = b'53 55 42 4D 49 54 31 00'        # "SUBMIT1"    | max size 13 C-Octet String)
    iface_version: bytes    = b'50'                             # 0x50         | Integer(1)
    addr_ton: bytes         = b'01'                             # 0x01         | Integer(1)
    addr_npi: bytes         = b'01'                             # 0x01         | Integer(1)
    addr_range: bytes       = b'00'                             # NULL         | max size 41 C-Octet String


@dataclass
class BindTransmitterPDUSample2(PDUSample):
    length: bytes           = b'00 00 00 17'  # 23, 0x00000017
    id: bytes               = b'00 00 00 02'
    status: bytes           = b'00 00 00 00'
    sequence: bytes         = b'00 00 00 01'
    sys_id: bytes           = b'00'
    password: bytes         = b'00'
    sys_type: bytes         = b'00'
    iface_version: bytes    = b'50'
    addr_ton: bytes         = b'01'
    addr_npi: bytes         = b'01'
    addr_range: bytes       = b'00'


@dataclass
class BindTransmitterPDUSample3(PDUSample):
    length: bytes           = b'00 00 00 64'  # 100, 0x00000064
    id: bytes               = b'00 00 00 02'
    status: bytes           = b'00 00 00 00'
    sequence: bytes         = b'00 00 00 01'
    sys_id: bytes           = str2bin('SMPP3TEST012345')
    password: bytes         = str2bin('PASSWORD1')
    sys_type: bytes         = str2bin('SYSTEMTYPE123')
    iface_version: bytes    = b'50'
    addr_ton: bytes         = b'01'
    addr_npi: bytes         = b'01'
    addr_range: bytes       = str2bin('Z' * 40)


# vim: sw=4:et:ai
