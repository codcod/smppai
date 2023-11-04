"""Constant values defined by SMPP protocol."""
import enum

from .operations import BindTransmitter
from .operations import BindTransmitterResp

# SMPP_CMD_ALERT_NOTIFICATION = 'alert_notification'
# SMPP_CMD_BIND_RECEIVER = 'bind_receiver'
# SMPP_CMD_BIND_RECEIVER_RESP = 'bind_receiver_resp'
# SMPP_CMD_BIND_TRANSCEIVER = 'bind_transceiver'
# SMPP_CMD_BIND_TRANSCEIVER_RESP = 'bind_transceiver_resp'
# SMPP_CMD_BIND_TRANSMITTER = 'bind_transmitter'
# SMPP_CMD_BIND_TRANSMITTER_RESP = 'bind_transmitter_resp'
# SMPP_CMD_CANCEL_SM = 'cancel_sm'
# SMPP_CMD_CANCEL_SM_RESP = 'cancel_sm_resp'
# SMPP_CMD_DATA_SM = 'data_sm'
# SMPP_CMD_DATA_SM_RESP = 'data_sm_resp'
# SMPP_CMD_DELIVER_SM = 'deliver_sm'
# SMPP_CMD_DELIVER_SM_RESP = 'deliver_sm_resp'
# SMPP_CMD_ENQUIRE_LINK = 'enquire_link'
# SMPP_CMD_ENQUIRE_LINK_RESP = 'enquire_link_resp'
# SMPP_CMD_GENERIC_NACK = 'generic_nack'
# SMPP_CMD_OUTBIND = 'outbind'
# SMPP_CMD_QUERY_SM = 'query_sm'
# SMPP_CMD_QUERY_SM_RESP = 'query_sm_resp'
# SMPP_CMD_REPLACE_SM = 'replace_sm'
# SMPP_CMD_REPLACE_SM_RESP = 'replace_sm_resp'
# SMPP_CMD_SUBMIT_MULTI = 'submit_multi'
# SMPP_CMD_SUBMIT_MULTI_RESP = 'submit_multi_resp'
# SMPP_CMD_SUBMIT_SM = 'submit_sm'
# SMPP_CMD_SUBMIT_SM_RESP = 'submit_sm_resp'
# SMPP_CMD_UNBIND = 'unbind'
# SMPP_CMD_UNBIND_RESP = 'unbind_resp'


class OperationID(enum.Enum):
    """Operation ID and a class representing this operation."""

    BIND_TRANSMITTER = 0x00000002, BindTransmitter
    BIND_TRANSMITTER_RESP = 0x80000002, BindTransmitterResp

    @classmethod
    def get_operation(cls, id):
        """Use Operation id to return class representing this Operation."""
        for m in cls.__members__:
            id_, klass = (getattr(cls, m)).value
            if id_ == id:
                return klass


# vim: sw=4:et:ai
