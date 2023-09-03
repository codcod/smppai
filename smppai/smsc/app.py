"""SMSC server"""
import asyncio
import logging
import time
from asyncio import StreamReader, StreamWriter

import smppai.smpp as smpp

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(module)s:%(lineno)s] %(message)s',
    datefmt='%d/%m/%Y %H:%M:%S %Z',
)
logging.Formatter.converter = time.localtime
logging.getLogger('asyncio').disabled = True

# save received text messages in a file
store = logging.getLogger('store')
store.setLevel(logging.DEBUG)
fh = logging.FileHandler('store.log')
fh.setFormatter(
    logging.Formatter('%(asctime)s %(message)s', datefmt='%d/%m/%Y %H:%M:%S %Z')
)
store.addHandler(fh)


class SMSC:
    async def start_server(self, host: str, port: int):
        server = await asyncio.start_server(self.client_connected, host, port)
        async with server:
            await server.serve_forever()

    async def client_connected(self, reader: StreamReader, writer: StreamWriter):
        logging.debug(f'Client connected')

        data = await smpp.read_data(reader)
        pdu = smpp.unpack(data)
        logging.debug(f'PDU = {pdu=}')

        match type(pdu):
            case smpp.BindTransmitter:
                logging.debug('Received command: bind_transmitter')
                await self.on_connect_transmitter(pdu.sys_id, writer)
                asyncio.create_task(self._listen_for_requests(reader, writer))
            case _:
                logging.error('Got invalid command from client, disconnecting')
                writer.close()
                await writer.wait_closed()

    async def on_connect_transmitter(self, system_id: str, writer: StreamWriter):
        logging.debug(f'Called on_connect_transmitter for [{system_id}]')
        params = {'status': 0x00000000, 'sys_id': 'login'}
        pdu = smpp.BindTransmitterResp(**params)
        logging.debug(f'BindTransmitterResp to send = {pdu=}')
        await smpp.send_data(pdu, writer)

    async def _listen_for_requests(self, reader: StreamReader, writer: StreamWriter):
        logging.debug(f'Listening for requests now')
        try:
            while (data := await asyncio.wait_for(smpp.read_data(reader), 60)) != b'':
                logging.debug(f'Received data [{data}]')
                pdu = smpp.parse_pdu(data, client=smpp.Sequence())
                await self.process_request(pdu, writer)
        except ConnectionResetError as e:
            logging.exception(
                'Client disconnected while processing commands', exc_info=e
            )
        except Exception as e:
            logging.exception('Error reading from client.', exc_info=e)

    async def process_request(self, pdu: smpp.Operation, writer):
        logging.debug(f'Processing request: [{pdu}]')
        match type(pdu):
            # case commands.EnquireLink:
            #     logging.debug(f'Received command enquire_link')
            #     await smpp.send_data('enquire_link_resp', writer)
            # case commands.SubmitSM:
            #     logging.debug(f'Received command submit_sm')
            #     logging.debug(
            #         f'\n    PDU = [{pdu}]\n'
            #         f'    short_message = [{pdu.short_message}]'
            #         f'->[{pdu.short_message.decode()}]\n'
            #         f'    sequence = [{pdu.sequence}]\n'
            #         f'    status = [{pdu.status}: {pdu.get_status_desc()}]'
            #     )
            #     store.debug(f'| {pdu.short_message.decode()} | from: {pdu.source_addr} | to: {pdu.destination_addr} |')
            #     await smpp.send_data('submit_sm_resp', writer)
            # case commands.Unbind:
            #     logging.debug(f'Received command unbind')
            #     await smpp.send_data('unbind_resp', writer)
            case _:
                logging.error(
                    'Unrecognized command from client while processing requests, disconnecting'
                )
                writer.close()
                await writer.wait_closed()


async def main():
    port = 2775
    logging.info(f'Starting SMSC server on port {port}')

    app = SMSC()
    await app.start_server('127.0.0.1', port)


try:
    asyncio.run(main())
except KeyboardInterrupt:
    logging.info('Stopping SMSC server...')

# vim: sw=4:et:ai
