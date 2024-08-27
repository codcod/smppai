import binascii
import logging
import socket
import struct

import smpplib

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# class Connection:
#     def __init__(self,
#             address,
#             family=socket.AF_INET,
#             type=socket.SOCK_STREAM,
#             timeout=3
#     ):
#         self.address = address
#         self.family = socket.AF_INET
#         self.type = socket.SOCK_STREAM
#         self.local = threading.local()
#         self._timeout = timeout

#     def __enter__(self):
#         if hasattr(self.local, 'sock'):
#             raise RuntimeError('Already connected')
#         logger.error('socket conneted')
#         self.local.sock = socket.socket(self.family, self.type)
#         self.local.sock.settimeout(self._timeout)
#         self.local.sock.connect(self.address)
#         return self.local.sock

#     def __exit__(self, exc_ty, exc_val, tb):
#         logger.error('socket closed')
#         self.local.sock.close()
#         del self.local.sock


class Connection:
    def __init__(
        self, address, family=socket.AF_INET, type=socket.SOCK_STREAM, timeout=10
    ):
        self.address = address
        self.family = family
        self.type = type
        self.sock = None
        self.timeout = timeout

    def __enter__(self):
        if self.sock is not None:
            raise RuntimeError('Already connected')
        self.sock = socket.socket(self.family, self.type)
        self.sock.settimeout(self.timeout)
        self.sock.connect(self.address)
        return self.sock

    def __exit__(self, exc_ty, exc_val, tb):
        self.sock.close()
        self.sock = None


class default_client(object):
    sequence = 0

    def next_sequence(self):
        return 1


def bind(sock, command_name, **kwargs):
    if command_name in ('bind_receiver', 'bind_transceiver'):
        logger.debug('Receiver mode')

    logger.info(f'{kwargs=}')

    p = smpplib.smpp.make_pdu(command_name, client=default_client(), **kwargs)

    send_pdu(sock, p)
    try:
        logger.warning('sending bind')
        resp = read_pdu(sock)
    except socket.timeout:
        raise smpplib.exceptions.ConnectionError()
    if resp.is_error():
        raise smpplib.exceptions.PDUError(
            '({}) {}: {}'.format(
                resp.status,
                resp.command,
                smpplib.consts.DESCRIPTIONS.get(resp.status, 'Unknown code'),
            ),
            int(resp.status),
        )
    return resp


def bind2(conn, command_name, **kwargs):
    if command_name in ('bind_receiver', 'bind_transceiver'):
        logger.debug('Receiver mode')

    p = smpplib.smpp.make_pdu(command_name, client=default_client(), **kwargs)

    with conn as sock:
        send_pdu(sock, p)
        try:
            logger.warning('sending bind')
            resp = read_pdu(sock)
        except socket.timeout:
            raise smpplib.exceptions.ConnectionError()
        if resp.is_error():
            raise smpplib.exceptions.PDUError(
                '({}) {}: {}'.format(
                    resp.status,
                    resp.command,
                    smpplib.consts.DESCRIPTIONS.get(resp.status, 'Unknown code'),
                ),
                int(resp.status),
            )
        return resp


def send_pdu(sock, p):
    # if self.state not in consts.COMMAND_STATES[p.command]:
    #     raise exceptions.PDUError("Command %s failed: %s" % (
    #         p.command,
    #         consts.DESCRIPTIONS[consts.SMPP_ESME_RINVBNDSTS],
    #     ))

    logger.warning('Sending %s PDU', p.command)
    generated = p.generate()
    logger.debug('>>%s (%d bytes)', binascii.b2a_hex(generated), len(generated))

    try:
        sock.sendall(generated)
    except socket.error as e:
        logger.warning(e)
        raise smpplib.exceptions.ConnectionError()

    return True


def _recv_exact(sock, exact_size):
    parts = []
    received = 0
    logger.debug('_recv_exact')
    while received < exact_size:
        try:
            logger.debug(f'{received=}')
            part = sock.recv(exact_size - received)
            logger.debug(f'{part=}')
        except socket.timeout:
            logger.debug('timeout')
            raise
        except socket.error as e:
            logger.warning(e)
            raise smpplib.exceptions.ConnectionError()
        if not part:
            raise smpplib.exceptions.ConnectionError()
        received += len(part)
        parts.append(part)
    return b"".join(parts)


def read_pdu(sock):
    logger.debug('Waiting for PDU...')

    raw_len = _recv_exact(sock, 4)
    logger.debug(f'{raw_len=}')

    try:
        length = struct.unpack('>L', raw_len)[0]
    except struct.error:
        logger.warning('Receive broken pdu... %s', repr(raw_len))

    raw_pdu = raw_len + _recv_exact(sock, length - 4)

    logger.debug('<<%s (%d bytes)', binascii.b2a_hex(raw_pdu), len(raw_pdu))

    pdu = smpplib.smpp.parse_pdu(
        raw_pdu,
        client=default_client(),
        allow_unknown_opt_params=True,
    )

    logger.debug('Read %s PDU', pdu.command)

    if pdu.is_error():
        return pdu

    elif pdu.command in smpplib.consts.STATE_SETTERS:
        logger.debug(f'state = {smpplib.consts.STATE_SETTERS[pdu.command]}')

    return pdu


def read_once(sock, ignore_error_codes=None, auto_send_enquire_link=True):
    logger.debug('READ_ONCE')
    try:
        try:
            pdu = read_pdu(sock)
        except socket.timeout:
            if not auto_send_enquire_link:
                raise
            logger.debug('Socket timeout, listening again')
            pdu = smpplib.smpp.make_pdu('enquire_link', client=default_client())
            send_pdu(sock, pdu)
            return

        if pdu.is_error():
            logger.debug('error_pdu_handler(pdu)')

        if pdu.command == 'unbind':  # unbind_res
            logger.info('Unbind command received')
            return
        elif pdu.command == 'submit_sm_resp':
            logger.info('message_sent_handler(pdu=pdu)')
        elif pdu.command == 'deliver_sm':
            logger.info('_message_received(pdu)')
        elif pdu.command == 'query_sm_resp':
            logger.info('query_resp_handler(pdu)')
        elif pdu.command == 'enquire_link':
            logger.info('_enquire_link_received(pdu)')
        elif pdu.command == 'enquire_link_resp':
            pass
        elif pdu.command == 'alert_notification':
            logger.info('_alert_notification(pdu)')
        else:
            logger.warning('Unhandled SMPP command "%s"', pdu.command)
    except smpplib.exceptions.PDUError as e:
        if ignore_error_codes and len(e.args) > 1 and e.args[1] in ignore_error_codes:
            logger.warning('(%d) %s. Ignored.', e.args[1], e.args[0])
        else:
            raise


def listen(conn):
    with conn as s:
        while True:
            read_once(s)


def listen2(s):
    while True:
        read_once(s)


if __name__ == '__main__':
    with Connection(('127.0.0.1', 2775)) as s:
        bind(s, 'bind_transceiver', system_id='smppclient1', password='password')
        while True:
            read_once(s)

    # conn = Connection(('127.0.0.1', 2775))
    # bind2(conn, 'bind_transceiver', system_id='smppclient1', password='password')
    # t = threading.Thread(target=listen, args=(conn, ))
    # t.start()

    # conn = Connection(('127.0.0.1', 2775))
    # with conn as s:
    #     bind(s, 'bind_transceiver', system_id='smppclient1', password='password')
    #     t = threading.Thread(target=listen2, args=(s, ))
    #     t.start()
