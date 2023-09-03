import logging
import threading
import time
import pytest

import smpplib.client
import smpplib.consts
import smpplib.gsm

logging.basicConfig(level=logging.DEBUG)


def message_sent(pdu):
    logging.warning(f'sent {pdu.sequence} {pdu.message_id}')


def message_received(pdu):
    logging.warning(f'delivered: {pdu.short_message}')


def send_message(client, message: str, sender: str, receiver: str):
    # Two parts, UCS2, SMS with UDH
    parts, encoding_flag, msg_type_flag = smpplib.gsm.make_parts(message)
    print(f'Sending message, parts = {parts}')

    for part in parts:
        pdu = client.send_message(
            source_addr_ton=smpplib.consts.SMPP_TON_INTL,
            # source_addr_npi=smpplib.consts.SMPP_NPI_ISDN,
            # Make sure it is a byte string, not unicode:
            source_addr=sender,
            dest_addr_ton=smpplib.consts.SMPP_TON_INTL,
            # dest_addr_npi=smpplib.consts.SMPP_NPI_ISDN,
            # Make sure thease two params are byte strings, not unicode:
            destination_addr=receiver,
            short_message=part,
            data_coding=encoding_flag,
            esm_class=msg_type_flag,
            registered_delivery=True,
        )
        print(pdu.sequence)


def test_send_message():
    client = smpplib.client.Client(
        'localhost', 2775, allow_unknown_opt_params=True
    )
    client.set_message_sent_handler(message_sent)
    client.set_message_received_handler(message_received)
    client.connect()
    logging.warning('CONNECTED')
    client.bind_transmitter(system_id='test_client', password='password')
    logging.warning('BOUND')

    # t = threading.Thread(target=client.listen)
    # t.start()
    # logging.warning('STARTED LISTENING FOR RESPONSES')
    # print('STARTED LISTENING FOR RESPONSES')
    # for i in range(10**3):
    #     send_message(client, 'Hello_' + str(i), 'Me', 'You')
    #     logging.warning('SENT MESSAGE')
    # t.join()

    logging.warning('BEFORE UNBIND')
    client.unbind()
    logging.warning('UNBOUND')
    time.sleep(1)
    logging.warning('BEFORE DISCONNECT')
    client.disconnect()
    logging.warning('DISCONNECTED')

    assert True


# vim: sw=4:et:ai
