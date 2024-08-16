import logging

import smpplib

logger = logging.getLogger('decoder')

PDU = smpplib.pdu.PDU


class sequencer:
    def next_sequence(self):
        return 1


def decode(data: bytes) -> PDU:
    pdu = smpplib.smpp.parse_pdu(
        data,
        client=sequencer(),
        allow_unknown_opt_params=True,
    )
    return pdu
