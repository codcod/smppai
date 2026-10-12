"""
Simulator SMSC, for testing an ESME without a carrier

Accepts any bind, answers each submit_sm that asks for a delivery receipt
with one after a delay and a weighted-random outcome, and injects MO from
POST /mo. For testing only: binds and HTTP are unauthenticated.

    python -m smpp.sim --receipt-delay 0.5 --stat DELIVRD:9 --stat UNDELIV:1
    curl -X POST 'localhost:2776/mo?from=%2B306900000001&to=1234&text=hi'

In-process (tests):

    sim = Simulator('127.0.0.1', 0, http_port=0, setup_signal_handlers=False)
    await sim.start()
    ...  # connect to sim.port; POST to sim.http_port
    await sim.stop()
"""

import argparse
import asyncio
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import logging
import random
import threading
import typing as tp
from urllib.parse import parse_qs, urlsplit
import uuid

from .exceptions import SMPPPDUException
from .message import _STAT_TO_STATE, Address, Message
from .protocol import DataCoding
from .protocol.codec import encode_message_with_encoding
from .server import ClientSession, Server, Shutdown

__all__ = ['Simulator', 'main']

logger = logging.getLogger(__name__)

Stat = tp.Tuple[str, int]

_DATE = '%y%m%d%H%M'


class Simulator:
    """An SMSC that sends receipts by itself; wraps smpp.Server, as `server`."""

    def __init__(
        self,
        host: str = '127.0.0.1',
        port: int = 2775,
        *,
        http_port: tp.Optional[int] = None,
        receipt_delay: float = 1.0,
        stats: tp.Sequence[Stat] = (('DELIVRD', 1),),
        **server_kwargs,
    ):
        """
        Args:
            http_port: Port for POST /mo; None = no HTTP, 0 = ephemeral
            receipt_delay: Seconds between submit_sm and its receipt
            stats: (stat, weight) pairs to draw each outcome from; the stat
                'NONE' sends no receipt
            **server_kwargs: Extra SMPPServer constructor arguments
        """
        self.host = host
        self.port = port
        self.http_port = http_port
        self.receipt_delay = receipt_delay
        self._stats = [s for s, _ in stats]
        self._weights = [w for _, w in stats]
        self._tasks: tp.Set[asyncio.Task] = set()
        self._http: tp.Optional[ThreadingHTTPServer] = None
        self.server = Server(
            host,
            port,
            shutdown=Shutdown(grace=1, reminder=1, timeout=5),
            **server_kwargs,
        )
        self.server.on_submit(self._on_submit)

    def _on_submit(self, session: ClientSession, msg: Message) -> str:
        # Generated here, not by the server: the receipt must carry the same id
        # as submit_sm_resp, and it stays unique across simulator restarts
        message_id = uuid.uuid4().hex
        stat = random.choices(self._stats, self._weights)[0]  # nosec B311
        wanted = msg.pdu.registered_delivery & 0x03
        logger.info(
            'submit %s from %s: %s -> %s, stat %s',
            message_id,
            session.system_id,
            msg.sender.addr,
            msg.to.addr,
            stat,
        )
        if stat != 'NONE' and (wanted == 1 or (wanted == 2 and stat != 'DELIVRD')):
            task = asyncio.create_task(
                self._receipt(session.system_id, msg, message_id, stat, datetime.now())
            )
            self._tasks.add(task)
            task.add_done_callback(self._tasks.discard)
        return message_id

    async def _receipt(
        self,
        system_id: str,
        msg: Message,
        message_id: str,
        stat: str,
        submitted: datetime,
    ) -> None:
        await asyncio.sleep(self.receipt_delay)
        ok = stat == 'DELIVRD'
        # Receipts go out as GSM-7: swap what it can't carry for '?'
        snippet = (msg.text or '')[:20].encode('gsm0338', 'replace').decode('gsm0338')
        text = (
            f'id:{message_id} sub:001 dlvrd:{"001" if ok else "000"} '
            f'submit date:{submitted:{_DATE}} done date:{datetime.now():{_DATE}} '
            f'stat:{stat} err:{"000" if ok else "001"} text:{snippet}'
        )
        sent = await self.server.raw.deliver_sm(
            target_system_id=system_id,
            source_addr=msg.to.addr,
            destination_addr=msg.sender.addr,
            short_message=text,
            source_addr_ton=msg.to.ton,
            source_addr_npi=msg.to.npi,
            dest_addr_ton=msg.sender.ton,
            dest_addr_npi=msg.sender.npi,
            esm_class=0x04,
        )
        if sent:
            logger.info('receipt %s %s to %s', message_id, stat, system_id)
        else:
            logger.warning(
                'receipt %s dropped: not delivered to %s', message_id, system_id
            )

    async def mo(
        self, sender: str, to: str, text: str, system_id: tp.Optional[str] = None
    ) -> bool:
        """
        Deliver an MO message to system_id, or to the first bound receiver
        or transceiver; False when none is bound or the ESME refused it.
        """
        if system_id is None:
            receivers = [
                s
                for s in self.server.raw.get_bound_clients()
                if s.bind_type in ('receiver', 'transceiver')
            ]
            if not receivers:
                logger.warning('MO %s -> %s dropped: no receiver bound', sender, to)
                return False
            system_id = receivers[0].system_id
        src, dst = Address.parse(sender), Address.parse(to)
        try:
            encode_message_with_encoding(text, DataCoding.DEFAULT)
            data_coding = DataCoding.DEFAULT
        except SMPPPDUException:
            data_coding = DataCoding.UCS2
        ok = await self.server.raw.deliver_sm(
            target_system_id=system_id,
            source_addr=src.addr,
            destination_addr=dst.addr,
            short_message=text,
            source_addr_ton=src.ton,
            source_addr_npi=src.npi,
            dest_addr_ton=dst.ton,
            dest_addr_npi=dst.npi,
            data_coding=data_coding,
        )
        logger.info(
            'MO %s -> %s to %s: %s', sender, to, system_id, 'ok' if ok else 'refused'
        )
        return ok

    def _start_http(self) -> None:
        if self.http_port is None:
            return
        loop = asyncio.get_running_loop()
        sim = self

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self) -> None:
                url = urlsplit(self.path)
                if url.path != '/mo':
                    return self._reply(404, 'not found')
                params = parse_qs(url.query)
                length = int(self.headers.get('Content-Length') or 0)
                if length:  # a form body, as curl -d sends
                    params.update(parse_qs(self.rfile.read(length).decode()))
                p = {k: v[0] for k, v in params.items()}
                if not all(p.get(k) for k in ('from', 'to', 'text')):
                    return self._reply(400, 'from, to and text are required')
                ok = asyncio.run_coroutine_threadsafe(
                    sim.mo(p['from'], p['to'], p['text'], p.get('system_id')), loop
                ).result(timeout=35)
                if ok:
                    self._reply(200, 'ok')
                else:
                    self._reply(409, 'no receiver bound, or the ESME refused it')

            def _reply(self, code: int, body: str) -> None:
                data = (body + '\n').encode()
                self.send_response(code)
                self.send_header('Content-Type', 'text/plain; charset=utf-8')
                self.send_header('Content-Length', str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def log_message(self, format: str, *args: tp.Any) -> None:
                logger.debug(format, *args)

        self._http = ThreadingHTTPServer((self.host, self.http_port), Handler)
        self.http_port = self._http.server_address[1]
        threading.Thread(target=self._http.serve_forever, daemon=True).start()
        logger.info('MO endpoint on http://%s:%d/mo', self.host, self.http_port)

    async def _cleanup(self) -> None:
        if self._http is not None:
            await asyncio.to_thread(self._http.shutdown)
            self._http.server_close()
            self._http = None
        for task in self._tasks:
            task.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)

    async def start(self) -> None:
        await self.server.start()
        listener = self.server.raw._server
        if listener is not None:  # the real port, when started on port 0
            self.port = listener.sockets[0].getsockname()[1]
        self._start_http()

    async def stop(self) -> None:
        await self._cleanup()
        await self.server.stop()

    async def serve_forever(self) -> None:
        """Serve SMPP and HTTP until SIGINT/SIGTERM or server.stop()."""
        self._start_http()
        try:
            await self.server.serve_forever()
        finally:
            await self._cleanup()


def _stat(s: str) -> Stat:
    name, _, weight = s.partition(':')
    name = name.upper()
    if name != 'NONE' and name not in _STAT_TO_STATE:
        raise argparse.ArgumentTypeError(
            f'unknown stat {name!r}; use one of {", ".join(_STAT_TO_STATE)} or none'
        )
    if not weight:
        return name, 1
    if not weight.isdigit() or int(weight) < 1:
        raise argparse.ArgumentTypeError(f'weight must be a positive int: {s!r}')
    return name, int(weight)


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog='python -m smpp.sim',
        description='Simulator SMSC: answers submit_sm with delivery receipts and '
        'injects MO from POST /mo. For testing only: any bind is accepted and '
        'HTTP is unauthenticated.',
    )
    p.add_argument(
        '--host', default='127.0.0.1', help='bind address (default: %(default)s)'
    )
    p.add_argument(
        '--port', type=int, default=2775, help='SMPP port (default: %(default)s)'
    )
    p.add_argument(
        '--http-port',
        type=int,
        default=2776,
        help='POST /mo port (default: %(default)s)',
    )
    p.add_argument(
        '--receipt-delay',
        type=float,
        default=1.0,
        help='seconds before a receipt (default: %(default)s)',
    )
    p.add_argument(
        '--stat',
        type=_stat,
        action='append',
        metavar='STAT[:WEIGHT]',
        help='receipt outcome, repeatable, weighted (default: DELIVRD); '
        '"none" sends no receipt',
    )
    return p


def main(argv: tp.Optional[tp.Sequence[str]] = None) -> None:
    args = _parser().parse_args(argv)
    logging.basicConfig(
        level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s'
    )
    sim = Simulator(
        args.host,
        args.port,
        http_port=args.http_port,
        receipt_delay=args.receipt_delay,
        stats=args.stat or [('DELIVRD', 1)],
    )
    asyncio.run(sim.serve_forever())


if __name__ == '__main__':
    main()
