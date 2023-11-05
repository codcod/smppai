import logging

import smpplib
from smpplib import gsm

logger = logging.getLogger(__name__)

PDU = smpplib.pdu.PDU


class sequencer:
    def next_sequence(self):
        return 1


def bind_transceiver(**kwargs) -> PDU:
    assert 'system_id' in kwargs
    assert 'password' in kwargs

    logger.debug(f'encode <bind_transceiver> using {kwargs=}')
    p = smpplib.smpp.make_pdu('bind_transceiver', client=sequencer(), **kwargs)
    return p


def unbind() -> PDU:
    logger.debug('encode <unbind> using no kwargs')
    p = smpplib.smpp.make_pdu('unbind', client=sequencer())
    return p


def enquire_link() -> PDU:
    logger.debug('encode <enquire_link> using no kwargs')
    p = smpplib.smpp.make_pdu('enquire_link', client=sequencer())
    return p


def submit_sm(**kwargs) -> list[PDU]:
    assert 'source_addr' in kwargs
    assert 'destination_addr' in kwargs
    assert 'short_message' in kwargs

    logger.debug(f'encode <submit_sm> using {kwargs=}')

    message = kwargs['short_message']

    pdus = []
    parts, encoding_flag, msg_type_flag = gsm.make_parts(message)
    for part in parts:
        params = {
            'source_addr': kwargs['source_addr'],
            'destination_addr': kwargs['destination_addr'],
            'short_message': part,
            'data_coding': encoding_flag,
            'esm_class': msg_type_flag,
            'source_addr_ton': smpplib.consts.SMPP_TON_INTL,
            'dest_addr_ton': smpplib.consts.SMPP_TON_INTL,
            'registered_delivery': True,
        }
        pdu = smpplib.smpp.make_pdu('submit_sm', client=sequencer(), **params)
        logger.debug(f'appending {pdu=} to pdus list')
        pdus.append(pdu)
    return pdus
