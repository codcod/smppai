"""
High-level SMPP server API

A thin layer over SMPPServer: shutdown settings in the constructor and
decorator-registered handlers, sync or async.

    server = smpp.Server(port=2775, shutdown=smpp.Shutdown(grace=10, reminder=5))

    @server.authenticate
    async def auth(system_id, password, system_type):
        return password == 'secret'

    @server.on_submit
    async def on_submit(session, msg):
        print(msg.sender.addr, msg.text)

    await server.serve_forever()
"""

from dataclasses import dataclass
from typing import Awaitable, Callable, Optional, Union

from ..message import Message, _decode, _split, _to_message
from ..protocol import SubmitSm
from .server import ClientSession, SMPPServer

__all__ = ['Server', 'Shutdown']

Authenticate = Callable[[str, str, str], Union[bool, Awaitable[bool]]]
OnSubmit = Callable[
    [ClientSession, Message], Union[Optional[str], Awaitable[Optional[str]]]
]


@dataclass(frozen=True)
class Shutdown:
    """Graceful shutdown settings; see SMPPServer.configure_shutdown."""

    grace: float = 30.0
    reminder: float = 10.0
    timeout: float = 30.0


class Server:
    """High-level server; wraps an SMPPServer, exposed as `raw`."""

    def __init__(
        self,
        host: str = 'localhost',
        port: int = 2775,
        *,
        shutdown: Optional[Shutdown] = None,
        **server_kwargs,
    ):
        """
        Args:
            shutdown: Graceful shutdown settings (default: SMPPServer's)
            **server_kwargs: Extra SMPPServer constructor arguments
        """
        self.raw = SMPPServer(host, port, **server_kwargs)
        if shutdown is not None:
            self.raw.configure_shutdown(
                grace_period=shutdown.grace,
                reminder_delay=shutdown.reminder,
                shutdown_timeout=shutdown.timeout,
            )

    def authenticate(self, fn: Authenticate) -> Authenticate:
        """
        Register fn(system_id, password, system_type) -> bool as the bind
        check; replaces any earlier one.
        """
        self.raw.authenticate = fn
        return fn

    def on_submit(self, fn: OnSubmit) -> OnSubmit:
        """
        Register fn(session, msg: Message) -> message_id | None, called once
        per inbound submit_sm part; replaces any earlier one. Returning None
        keeps the server-generated message_id.
        """

        def adapter(
            raw: SMPPServer, session: ClientSession, pdu: SubmitSm
        ) -> Union[Optional[str], Awaitable[Optional[str]]]:
            text = _decode(_split(pdu)[1], pdu.data_coding)
            return fn(session, _to_message(pdu, text))

        self.raw.on_message_received = adapter
        return fn

    async def start(self) -> None:
        await self.raw.start()

    async def stop(self) -> None:
        await self.raw.stop()

    async def serve_forever(self) -> None:
        await self.raw.serve_forever()

    async def __aenter__(self) -> 'Server':
        await self.raw.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.raw.stop()
