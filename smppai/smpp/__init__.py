"""Helper functions to operate with SMPP protocol's PDUs."""

import asyncio
import binascii
import struct
import logging
from .proto import Operation
from .operations import BindTransmitter

__all__ = ['unpack', 'pack', 'BindTransmitter']


def unpack(frame: bytes) -> Operation:
    """Create PDU out of binary frame (factory method)."""
    # pdu = BindTransmitter()
    # pdu.load(frame)
    # return pdu
    raise NotADirectoryError()


def pack(operation: Operation) -> bytes:
    """Pack any PDU into bytes."""
    return operation.frame


async def read_data(stream: asyncio.streams.StreamReader) -> bytes:
    """Read data (PDU) from the client/connection stream.

    At first peek the PDU length from the PDU's header. Then read the rest of
    the data.
    """
    try:
        peek_size = 16
        peek = await stream.readexactly(peek_size)
        length = struct.unpack('>I', peek[:4])[0]
        data = peek + await stream.readexactly(length - peek_size)

        logging.debug('<<%s (%d bytes)', binascii.b2a_hex(data), length)
    except asyncio.streams.exceptions.IncompleteReadError as e:
        logging.exception('Error while reading from client', exc_info=e)
        data = b''

    return data  # binary pdu


async def send_data(operation: Operation, writer: asyncio.streams.StreamWriter):
    """Send PDU frame to client/connection stream."""
    writer.write(pack(operation))
    await writer.drain()


class Sequence(object):
    """Sequence generator used while preparing PDU."""

    MIN_SEQUENCE = 0x00000001
    MAX_SEQUENCE = 0x7FFFFFFF

    def __init__(self):
        self._sequence = self.MIN_SEQUENCE

    @property
    def sequence(self):
        return self._sequence

    def next_sequence(self):
        if self._sequence == self.MAX_SEQUENCE:
            self._sequence = self.MIN_SEQUENCE
        else:
            self._sequence += 1
        return self._sequence


# vim: sw=4:et:ai
