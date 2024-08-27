import argparse
import asyncio
import logging
import typing as tp

from smppai import log  # noqa: F401
from smppai.smpp import decoder
from smppai.smpp import encoder

logger = logging.getLogger('async_client')

HEADER_SIZE = 4


def enc_bind_transceiver() -> bytes:
    logger.debug('prepare to send <bind_transceiver>')
    params = {'system_id': 'smppclient1', 'password': 'password'}
    cmd = encoder.bind_transceiver(**params)
    pdu = cmd.generate()
    logger.debug(f'pdu to send: {pdu=}')
    return pdu


def enc_enquire_link() -> bytes:
    logger.debug('prepare to send <enquire_link>')
    params = {}
    cmd = encoder.enquire_link(**params)
    pdu = cmd.generate()
    logger.debug(f'pdu to send: {pdu=}')
    return pdu


def enc_submit_sm(src: str, dest: str, message: str) -> list[bytes]:
    logger.debug('prepare to send <submit_sm>')
    params = {
        'source_addr': src,
        'destination_addr': dest,
        'short_message': message,
    }
    cmds = encoder.submit_sm(**params)
    return [cmd.generate() for cmd in cmds]


async def send_msg(stream: asyncio.StreamWriter, data: bytes):
    stream.write(data)
    await stream.drain()


async def read_msg(stream: asyncio.StreamReader) -> bytes:
    header = await stream.readexactly(HEADER_SIZE)
    size = int.from_bytes(header, byteorder='big')
    payload = await stream.readexactly(size - HEADER_SIZE)
    return header + payload


async def listen_for_messages(stream: asyncio.StreamReader):
    while (pdu := await read_msg(stream)) != b'':
        cmd = decoder.decode(pdu)
        logger.debug(f'received in loop {pdu=}')
        logger.debug(f'received in loop {cmd=}')


async def main(args: tp.Sequence[str] | None = None):
    reader, writer = await asyncio.open_connection(args.host, args.port)

    await send_msg(writer, enc_bind_transceiver())

    message_listener = asyncio.create_task(listen_for_messages(reader))

    await send_msg(writer, enc_enquire_link())

    for pdu in enc_submit_sm('aa', 'bb', 'Hi'):
        await send_msg(writer, pdu)

    try:
        await asyncio.wait([message_listener])
    except Exception as e:
        logger.exception(e)
        logger.debug('close the connection')
        writer.close()
        await writer.wait_closed()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='localhost')
    parser.add_argument('--port', default=2775, type=int)
    try:
        asyncio.run(main(parser.parse_args()))
    except KeyboardInterrupt:
        print('Bye!')
