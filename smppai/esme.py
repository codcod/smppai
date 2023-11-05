import logging
import socket
import struct

import smpplib

from .smpp import decoder
from .smpp import encoder

logger = logging.getLogger(__name__)

PDU = smpplib.pdu.PDU

HEADER_SIZE: int = 4


class Connection:
    def __init__(
        self,
        address: tuple[str, int],
        family: int = socket.AF_INET,
        type: int = socket.SOCK_STREAM,
        timeout: int = 10,
    ):
        self._address = address
        self._family = family
        self._type = type
        self._sock = None
        self._timeout = timeout

    def connect(self):
        if self._sock is not None:
            raise RuntimeError('already connected')
        self._sock = socket.socket(self._family, self._type)
        self._sock.settimeout(self._timeout)
        self._sock.connect(self._address)
        logger.debug(f'connected: {self._address}')
        return self._sock

    def disconnect(self):
        self._sock.close()
        self._sock = None
        logger.debug(f'disconnected: {self._address}')

    def sendall(self, data: bytes):
        try:
            self._sock.sendall(data)
        except socket.error as e:
            logger.warning(e)
            raise ConnectionError()

    def recv(self, length: int = HEADER_SIZE) -> bytes:
        logger.debug(f'receiving {length=}')
        chunks = []
        bytes_received = 0
        while bytes_received < length:
            try:
                chunk = self._sock.recv(length - bytes_received)
                logger.debug(f'{chunk=}')
            except socket.timeout:
                logger.debug('timeout while receiving')
                raise
            except socket.error as e:
                logger.warning(e)
                raise smpplib.exceptions.ConnectionError()
            if not chunk:
                raise smpplib.exceptions.ConnectionError()
            bytes_received += len(chunk)
            chunks.append(chunk)
        return b''.join(chunks)


class ConnectionError(Exception):
    pass


class Esme:
    def __init__(self, *, host: str, port: int, username: str, password: str, **kwargs):
        self._conn: Connection = None
        self._host: str = host
        self._port: int = port
        self._username: str = username
        self._password: str = password

    def connect_to_smsc(self):
        self._conn = Connection(address=(self._host, self._port))
        self._conn.connect()

    def disconnect_from_smsc(self):
        self._conn.disconnect()

    def _send_pdu(self, cmd: PDU):
        logger.debug(f'sending pdu {cmd=}')
        self._conn.sendall(cmd.generate())

    def _recv_header(self) -> tuple[bytes, int]:
        header = self._conn.recv(HEADER_SIZE)
        length = struct.unpack('>L', header)[0]
        return header, length

    def _recv_pdu_bytes(self) -> bytes:
        logger.debug('receiving pdu')
        header, length = self._recv_header()
        payload = header + self._conn.recv(length - HEADER_SIZE)
        logger.debug(f'received {payload=!r}')
        return payload

    def recv_pdu(self) -> PDU:
        payload = self._recv_pdu_bytes()
        pdu = decoder.decode(payload)
        logger.info(f'received pdu {pdu=}')
        return pdu

    def listen_forever(self):
        while True:
            self.recv_pdu()

    def send_bind_transceiver(self):
        logger.debug('prepare to send <bind_transceiver>')
        params = {'system_id': self._username, 'password': self._password}
        cmd = encoder.bind_transceiver(**params)
        self._send_pdu(cmd)

    def unbind(self):
        logger.debug('prepare to send <unbind>')
        cmd = encoder.unbind()
        self._send_pdu(cmd)

    def send_submit_sm(self, src: str, dest: str, message: str):
        logger.debug('prepare to send <submit_sm>')
        params = {
            'source_addr': src,
            'destination_addr': dest,
            'short_message': message,
        }
        cmds = encoder.submit_sm(**params)
        for cmd in cmds:
            self._send_pdu(cmd)
            resp = self.recv_pdu()
            if type(resp) == smpplib.command.SubmitSMResp:
                logger.debug('<submit_sm> received')
            else:
                logger.warning('error while sending <submit_sm>')
