import dataclasses as dtc
import enum
import logging
import threading
from urllib.parse import urlparse

import smpplib

from .esme import Esme

logger = logging.getLogger(__name__)


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
        self._esme: Esme = None
        self._state: SessionState = SessionState.OPEN

    @property
    def state(self):
        return self._state

    def send_message(self, *, src: str, dest: str, message: str):
        logger.debug('sending message')
        self._esme.send_submit_sm(src, dest, message)
        logger.debug('message sent')

    def __enter__(self):
        logger.debug('entering session')
        params = self._cinfo.as_dict()
        self._esme = Esme(**params)
        self._esme.connect_to_smsc()
        if self._state == SessionState.OPEN:
            self._esme.send_bind_transceiver()
            
            resp = self._esme.recv_pdu()
            if type(resp) == smpplib.command.BindTransceiverResp:
                self._state = SessionState.BOUND_TRX
        
        # t = threading.Thread(target=self._esme.listen_forever)
        # t.start()
        
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        logger.debug('exiting session')
        assert self._esme is not None
        if self._state in (
            SessionState.BOUND_TRX,
            SessionState.BOUND_RX,
            SessionState.BOUND_TX,
        ):
            self._esme.unbind()
            self._esme.disconnect_from_smsc()
        else:
            logger.debug('already disconnected, silently closing connection')
        self._state = SessionState.CLOSED
        logger.debug('session exited')


def create_session(uri: str) -> Session:
    p = urlparse(uri)
    host = p.hostname if p.hostname else 'localhost'
    conn_info = ConnectionInfo(p.scheme, p.username, p.password, host, p.port)
    return Session(conn_info)
