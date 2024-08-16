import asyncio
import logging

HEADER_SIZE = 4

logger = logging.getLogger('proto')


async def send_data(stream: asyncio.StreamWriter, data: bytes):
    stream.write(data)
    logger.debug(f'data sent: {data=}')
    await stream.drain()


async def read_data(stream: asyncio.StreamReader) -> bytes:
    header = await stream.readexactly(HEADER_SIZE)
    size = int.from_bytes(header, byteorder='big')
    payload = await stream.readexactly(size - HEADER_SIZE)
    logger.debug(f'data read {header + payload}')
    return header + payload
