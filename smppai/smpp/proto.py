"""SMPP protocol.

Typing system to use when building PDUs defined by SMPP protocol. PDUs are
sometimes called Commands (SMPPv3), or Operations (SMPPv5).
"""
import struct
import collections
import typing as tp


NULL = b'\x00'


class Field:
    """Descriptor of a field that PDUs are made of."""

    def __init__(self, name, fmt, **opts):
        self.name = name
        self.fmt = fmt
        for key, value in opts.items():
            setattr(self, key, value)

    def __set__(self, instance, value):
        instance.__dict__[self.name] = value


def Typed(expected_type, cls=None):
    """Decorate descriptors to ensure the field is of expected type."""
    if cls is None:
        return lambda cls: Typed(expected_type, cls)

    super_set = cls.__set__

    def __set__(self, instance, value):
        if not isinstance(value, expected_type):
            raise TypeError('expected ' + str(expected_type))
        super_set(self, instance, value)

    cls.__set__ = __set__
    return cls


@Typed(int)
class Integer(Field):
    """Integer field."""

    ...


@Typed(str)
class String(Field):
    """Sting field."""

    ...


@Typed(bytes)
class Bytes(Field):
    """Bytes field."""

    ...


class OrderedMeta(type):
    """Metaclass to ensure fields are kept in order.

    Replaces default dict with OrderedDict.
    """

    def __new__(cls, clsname, bases, clsdict):
        """Create new instance."""
        d = dict(clsdict)
        order = []
        for name, value in clsdict.items():
            if isinstance(value, Field):
                value._name = name
                order.append(name)
        d['_order'] = order
        return type.__new__(cls, clsname, bases, d)

    @classmethod
    def __prepare__(cls, clsname, bases):
        return collections.OrderedDict()


def unpack_int(fmt: str, frame: bytes, offset: int) -> tp.Tuple[int, int]:
    """Unpack integer from frame."""
    r = struct.unpack_from(fmt, frame, offset)
    r = r[0] if len(r) == 1 else r
    return r, struct.calcsize(fmt)


def unpack_string(fmt: str, frame: bytes, offset: int) -> tp.Tuple[str, int]:
    """Unpack string from frame."""
    pos = frame[offset:].find(NULL)
    fmt_ = f'>{pos}s'
    r = struct.unpack(fmt_, frame[offset : offset + pos])
    r = r[0] if len(r) == 1 else r
    return r, pos + 1


class Operation(metaclass=OrderedMeta):
    """Base class for all PDUs/Operations."""

    # def __init__(self, bytesdata: bytes) -> None:
    #     self._buffer = memoryview(bytesdata)

    def dump(self) -> bytes:
        """Convert Operation to bytes."""
        raise NotImplementedError()

    def load(self, frame: bytes) -> None:
        """Parse frame and subesquently set all attributes of the Operation."""
        offset = 0
        for name in self._order:
            field = getattr(self, name)  # descriptor object
            if isinstance(field, Integer):
                val, size = unpack_int(field.fmt, frame, offset)
            elif isinstance(field, Bytes):
                val, size = unpack_string(field.fmt, frame, offset)
            offset += size
            setattr(self, name, val)

    def __repr__(self):
        result = [f'<{self.__class__.__name__}>']
        for i, name in enumerate(self._order):
            descr = getattr(self, name)
            if isinstance(descr, Integer):
                result.append(
                    f'<{i+1}: ' f'{name=} [{descr.name}, {descr.fmt}, {descr=}] '
                )
            elif isinstance(descr, int):
                result.append(f'<{i+1}: ' f'{name}={descr}')
        return '\n'.join(result)


# vim: sw=4:et:ai
