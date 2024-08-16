import asyncio
import dataclasses as dtc
import enum
import logging
from urllib.parse import urlparse

from smppai.proto import read_data
from smppai.proto import send_data
from smppai.smpp import decoder
from smppai.smpp import helpers
from smppai.smpp.encoder import PDU

logger = logging.getLogger('session')


@dtc.dataclass(frozen=True)
class ConnectionInfo:
    scheme: str
    username: str
    password: str
    host: str
    port: int = 2775

    as_dict = dtc.asdict

    def __str__(self):
        return '{}://{}@{}:{}'.format(self.scheme, self.username, self.host, self.port)


class SessionState(enum.Enum):
    OPEN = 'OPEN'
    BOUND_TX = 'BOUND_TX'
    BOUND_RX = 'BOUND_RX'
    BOUND_TRX = 'BOUND_TRX'
    CLOSED = 'CLOSED'


class Session:
    def __init__(self, connection_info: ConnectionInfo) -> None:
        self._cinfo = connection_info
        self._state: SessionState = SessionState.OPEN
        self._reader: asyncio.StreamReader = None
        self._writer: asyncio.StreamWriter = None
        self._message_listener: asyncio.Task = None

    @property
    def state(self):
        return self._state

    async def send_message(self, *, src: str, dest: str, message: str):
        logger.debug('sending message')
        for data in helpers.enc_submit_sm(src, dest, message):
            await send_data(self._writer, data)
        logger.debug('message sent')

    async def _send_enquire_link(self):
        data = helpers.enc_enquire_link()
        while True:
            await send_data(self._writer, data)
            await asyncio.sleep(10)

    async def _connect(self):
        if not all([self._reader, self._writer]):
            logger.debug('opening connection')
            self._reader, self._writer = await asyncio.open_connection(
                self._cinfo.host, self._cinfo.port
            )
        else:
            logger.warning('connection already opened')

    async def __aenter__(self):
        logger.debug('entering session')
        await self._connect()
        await send_data(self._writer, helpers.enc_bind_transceiver())

        return self

    async def __aexit__(self, exc_type, exc_value, exc_tb):
        logger.debug('exiting session')
        self._writer.close()
        await self._writer.wait_closed()
        logger.debug('session exited')

    async def __aiter__(self) -> PDU:
        # await self._connect()
        if self._reader:
            while True:
                try:
                    while (pdu := await read_data(self._reader)) != b'':
                        cmd = decoder.decode(pdu)
                        logger.debug(f'received in loop {pdu=}')
                        logger.debug(f'received in loop {cmd=}')
                        yield cmd
                except asyncio.exceptions.IncompleteReadError as e:
                    logger.warning(f'server closed: {e}')
                    break


def create_session(uri: str) -> Session:
    p = urlparse(uri)
    host = p.hostname if p.hostname else 'localhost'
    conn_info = ConnectionInfo(p.scheme, p.username, p.password, host, p.port)
    return Session(conn_info)
