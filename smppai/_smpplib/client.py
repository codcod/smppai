import collections
import select
import socket
from time import monotonic

from smpplib import exceptions
from smpplib import smpp
from smpplib.client import Client


class SessionProlongationDisabled(Exception):
    """Server send nothing and we do not want to continue"""


class ThreadSafeClient(Client):
    should_stop = False

    def __init__(self, *args, **kwargs):
        # Socket polling period
        select_timeout = kwargs.get('select_timeout', 1.0)

        super(ThreadSafeClient, self).__init__(*args, **kwargs)

        self._select_timeout = select_timeout

        self._send_queue = collections.deque()
        self._read_sock, self._send_sock = socket.socketpair()

        # It will help not to spam the server
        self._last_active_time = 0.0

    def accept(self, obj):
        """Accept an object"""
        raise NotImplementedError('not implemented')

    def send_pdu(self, pdu, send_later=False):
        if send_later:
            self._send_queue.append(pdu)
            self._send_sock.send(b'\x00')
            return True
        else:
            pdu_sent = super(ThreadSafeClient, self).send_pdu(pdu)
            self._last_active_time = monotonic()
            return pdu_sent

    def send_message(self, send_later=True, **kwargs):
        submit_sm_pdu = smpp.make_pdu('submit_sm', client=self, **kwargs)
        self.send_pdu(submit_sm_pdu, send_later=send_later)
        return submit_sm_pdu

    def _should_prolong_session(self):
        # We need some time to send enquire_link before the next `select` call comes
        passed_from_last_message = monotonic() - self._last_active_time

        return self.timeout - self._select_timeout <= passed_from_last_message

    def observe(self, ignore_error_codes=None, auto_send_enquire_link=True):
        while not self.should_stop:
            rlist, _, _ = select.select(
                [self._socket, self._read_sock],
                [],
                [],
                self._select_timeout,
            )

            if self.should_stop:
                break

            if not rlist:
                if self._should_prolong_session():
                    if not auto_send_enquire_link:
                        raise exceptions.SessionProlongationDisabled()

                    self.logger.debug('Sending enquire_link')
                    pdu = smpp.make_pdu('enquire_link', client=self)
                    self.send_pdu(pdu)
            else:
                for ready_socket in rlist:
                    if ready_socket is self._socket:
                        self.read_once(ignore_error_codes, auto_send_enquire_link)
                    else:
                        self._read_sock.recv(1)
                        self.send_pdu(self._send_queue.pop())

        self.logger.info('Finished observing...')

    # def __del__(self):
    #     print('THREADSAFECLIENT REMOVED')
    #     self.unbind()
    #     self.disconnect()
    #     return super().__del__()
