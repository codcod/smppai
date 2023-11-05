import logging

import smpplib

logger = logging.getLogger(__name__)

PDU = smpplib.pdu.PDU


class sequencer:
    def next_sequence(self):
        return 1


def decode(payload: bytes) -> PDU:
    pdu = smpplib.smpp.parse_pdu(
        payload,
        client=sequencer(),
        allow_unknown_opt_params=True,
    )
    return pdu
