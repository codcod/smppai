import logging

from smppai.smpp import encoder

logger = logging.getLogger('helpers')


def enc_bind_transceiver() -> bytes:
    logger.debug('prepare to send <bind_transceiver>')
    params = {'system_id': 'smppclient1', 'password': 'password'}
    data = encoder.bind_transceiver(**params)
    logger.debug(f'pdu to send: {data=}')
    return data


def enc_enquire_link() -> bytes:
    logger.debug('prepare to send <enquire_link>')
    params = {}
    data = encoder.enquire_link(**params)
    logger.debug(f'pdu to send: {data=}')
    return data


def enc_submit_sm(src: str, dest: str, message: str) -> list[bytes]:
    logger.debug('prepare to send <submit_sm>')
    params = {
        'source_addr': src,
        'destination_addr': dest,
        'short_message': message,
    }
    return encoder.submit_sm(**params)
