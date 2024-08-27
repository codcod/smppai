import logging
from functools import partial
from functools import singledispatch
from threading import Thread

from smpplib import command
from smpplib import consts
from smpplib import gsm
from smpplib.client import Client
from smpplib.pdu import PDU

from smppai import config
from smppai._smpplib.client import ThreadSafeClient

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@singledispatch
def handle_pdu(pdu: PDU):
    raise AttributeError(f'Unsupported type {type(pdu)}')


def _smsc_internal_message_id(short_message: bytes) -> str:
    # fmt: off
    # b'id:Smsc2108
    #   sub:1
    #   dlvrd:1
    #   submit
    #   date:2311011357
    #   done
    #   date:2311011357
    #   stat:DELIVRD
    #   err:0
    #   text:Hi 1000'
    # fmt: on
    step1 = (short_message.decode())
    step2 = step1.split()[0]  # 'id:Smsc2108'
    step3 = step2.split(':')[1]  # 'Smsc2108'
    return step3


@handle_pdu.register
def handle_deliver_sm(pdu: command.DeliverSM):
    logger.info(
        f'SMSC: message was delivered [{type(pdu)}] '
        f'{_smsc_internal_message_id(pdu.short_message)}\n'
    )


# fmt: off
# logger.info(
#     f'  {pdu.callback_num=}\n'
#     f'  {pdu.privacy_indicator=}\n'
#     f'  {pdu.sar_msg_ref_num=}\n'
#     f'  {pdu.user_message_reference=}\n'
#     f'  {pdu.message_payload=}\n'
#     f'  {pdu.short_message=}\n'
#     f'  {pdu.sm_length=}\n'
#     f'  {pdu.data_coding=}\n'
#     f'  {pdu.registered_delivery=}\n'
#     f'  {pdu.validity_period=}\n'
#     f'  {pdu.schedule_delivery_time=}\n'
#     # SMSC Delivery Receipt
#     f'  {pdu.source_addr=}\n'
#     f'  {pdu.destination_addr=}\n'
#     f'  {pdu.esm_class=}\n'
#     f'  {pdu.message_state=}\n'
#     f'  {pdu.network_error_code=}\n'
#     f'  {pdu.receipted_message_id=}\n'
# )
# [2023-11-01 14:57:36 +0100] [INFO] [app.py:28] [6116241408]
#   pdu.callback_num=None
#   pdu.privacy_indicator=None
#   pdu.sar_msg_ref_num=None
#   pdu.user_message_reference=None
#   pdu.message_payload=None
#   pdu.short_message=<see method above>
#   pdu.sm_length=101
#   pdu.data_coding=3
#   pdu.registered_delivery=0
#   pdu.validity_period=b''
#   pdu.schedule_delivery_time=b''
#   pdu.source_addr=b'321'
#   pdu.destination_addr=b'321'
#   pdu.esm_class=4
#   pdu.message_state=None
#   pdu.network_error_code=None
#   pdu.receipted_message_id=None
# fmt: on


@handle_pdu.register
def handle_submit_sm_resp(pdu: command.SubmitSMResp):
    int_message_id = pdu.message_id
    logger.info(f'SMSC: message was submitted [{type(pdu)}] {str(int_message_id)}')


def send_message(client: Client, sender: str, recipient: str, message: str):
    parts, encoding_flag, msg_type_flag = gsm.make_parts(message)
    for part in parts:
        pdu = client.send_message(
            source_addr=sender,
            destination_addr=recipient,
            short_message=part,
            data_coding=encoding_flag,
            esm_class=msg_type_flag,
            source_addr_ton=consts.SMPP_TON_INTL,
            dest_addr_ton=consts.SMPP_TON_INTL,
            registered_delivery=True,
        )
        logger.warning(f'PDU {pdu.sequence=}')


client = ThreadSafeClient(
    config.SERVER_HOST,
    config.SERVER_PORT,
    allow_unknown_opt_params=True,
    logger_name='smpp.Client',
    timeout=10,
)
client.set_message_received_handler(lambda pdu: handle_pdu(pdu))
client.set_message_sent_handler(lambda pdu: handle_pdu(pdu))

client.connect()
client.bind_transceiver(system_id='smppclient1', password='password')
client.send_message()

send = partial(send_message, client)

# try:
#     client.observe()  # enters into a loop
# except KeyboardInterrupt:
#     logger.error('Interrupted, exiting...')
# finally:
#     logger.error('Cleanig up, disconnecting...')
#     client.unbind()
#     client.disconnect()

t = Thread(target=client.observe)
t.start()

send(sender='123', recipient='321', message='Hi 1000')

if __name__ == '__main__':
    send(sender='123', recipient='321', message='Hi 1000')
    send(sender='123', recipient='321', message='Hi 2000')
    send(sender='123', recipient='321', message='Hi 3000')
    client.should_stop = True

    import time

    client.unbind()
    time.sleep(3)
    client.disconnect()
    time.sleep(3)
