"""SMPP PDU Operations."""

from .proto import Bytes
from .proto import Integer
from .proto import Operation


class BindTransmitter(Operation):
    """Bind Transmitter operation."""

    length = Integer('length', '>L')
    id = Integer('id', '>L')
    status = Integer('status', '>L')
    sequence = Integer('sequence', '>L')
    sys_id = Bytes('sys_id', '>16s')
    password = Bytes('password', '>9s')
    sys_type = Bytes('sys_type', '>13s')
    iface_version = Integer('iface_version', '>B')
    addr_ton = Integer('addr_ton', '>B')
    addr_npi = Integer('addr_npi', '>B')
    addr_range = Bytes('addr_range', '>41s')


class BindTransmitterResp(Operation):
    """Bind Transmitter Resp operation."""

    length = Integer('length', '>L')
    id = Integer('id', '>L')
    status = Integer('status', '>L')
    sequence = Integer('sequence', '>L')
    sys_id = Bytes('sys_id', '>16s')


# vim: sw=4:et:ai
