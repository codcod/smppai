"""In-process loopback benchmark: submit_sm throughput between an SMPPClient and SMPPServer.

Run: uv run python benchmarks/loopback.py [--n 5000] [--inflight 100] [--repeat 3] [--uvloop]
"""

import argparse
import asyncio
import logging
import socket
import time

from smpp import SMPPClient, SMPPServer


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]


async def _run_once(n: int, inflight: int) -> float:
    port = _free_port()
    server = SMPPServer('127.0.0.1', port, setup_signal_handlers=False)
    await server.start()

    client = SMPPClient('127.0.0.1', port, 'bench', 'pw')
    await client.connect()
    await client.bind_transmitter()

    sem = asyncio.Semaphore(inflight)

    async def send_one(i: int) -> None:
        async with sem:
            await client.submit_sm('1234', '5678', f'msg {i}')

    start = time.perf_counter()
    await asyncio.gather(*(send_one(i) for i in range(n)))
    elapsed = time.perf_counter() - start

    await client.unbind()
    await client.disconnect()
    await server.stop()
    return elapsed


async def _main(args: argparse.Namespace) -> None:
    logging.disable(logging.CRITICAL)
    best = min([await _run_once(args.n, args.inflight) for _ in range(args.repeat)])
    print(f'{args.n / best:.1f} msg/s, {best / args.n * 1e6:.1f} us/msg (best of {args.repeat})')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--n', type=int, default=5000)
    parser.add_argument('--inflight', type=int, default=100)
    parser.add_argument('--repeat', type=int, default=3)
    parser.add_argument('--uvloop', action='store_true')
    parsed = parser.parse_args()

    if parsed.uvloop:
        import uvloop

        uvloop.run(_main(parsed))
    else:
        asyncio.run(_main(parsed))
