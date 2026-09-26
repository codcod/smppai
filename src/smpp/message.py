"""
Message types shared by the high-level client and server APIs.

The client yields Message for inbound deliver_sm/data_sm; the server hands
one to on_submit for each inbound submit_sm.
"""

from dataclasses import dataclass
import typing as tp

from .exceptions import SMPPPDUException, SMPPValidationException
from .gsm import UDH, ConcatenatedSMSHeader
from .protocol import (
    DataSm,
    DeliverSm,
    MessageState,
    NpiType,
    OptionalTag,
    SubmitSm,
    TonType,
)
from .protocol.codec import decode_message_with_encoding

__all__ = ['Address', 'Message', 'DeliveryReceipt']


@dataclass(frozen=True)
class Address:
    """An SMPP address with its type of number and numbering plan."""

    addr: str
    ton: int = TonType.UNKNOWN
    npi: int = NpiType.UNKNOWN

    @classmethod
    def parse(cls, s: tp.Union[str, 'Address']) -> 'Address':
        """
        Parse an address string.

        Spaces and '-' are ignored in numbers. '+<digits>' is international
        ISDN, plain digits are unknown/unknown, anything else (including
        non-ASCII digits) is an alphanumeric sender, kept as given.
        """
        if isinstance(s, Address):
            return s
        n = s.replace(' ', '').replace('-', '')
        if n.startswith('+') and _ascii_digits(n[1:]):
            return cls(n[1:], TonType.INTERNATIONAL, NpiType.ISDN)
        if n == '' or _ascii_digits(n):
            return cls(n, TonType.UNKNOWN, NpiType.UNKNOWN)
        return cls(s, TonType.ALPHANUMERIC, NpiType.UNKNOWN)


def _ascii_digits(s: str) -> bool:
    return s.isascii() and s.isdigit()


@dataclass(frozen=True)
class DeliveryReceipt:
    """A parsed delivery receipt; TLVs take precedence over the receipt text."""

    id: tp.Optional[str] = None
    state: tp.Optional[MessageState] = None
    stat: tp.Optional[str] = None
    err: tp.Optional[str] = None
    submit_date: tp.Optional[str] = None
    done_date: tp.Optional[str] = None
    text: tp.Optional[str] = None


@dataclass(frozen=True)
class Message:
    """An inbound message, decoded (and, client-side, reassembled)."""

    sender: Address
    to: Address
    text: tp.Optional[str]
    receipt: tp.Optional[DeliveryReceipt]
    pdu: tp.Union[DeliverSm, DataSm, SubmitSm]

    @property
    def is_receipt(self) -> bool:
        return self.receipt is not None


_STAT_TO_STATE = {
    'DELIVRD': MessageState.DELIVERED,
    'EXPIRED': MessageState.EXPIRED,
    'DELETED': MessageState.DELETED,
    'UNDELIV': MessageState.UNDELIVERABLE,
    'ACCEPTD': MessageState.ACCEPTED,
    'UNKNOWN': MessageState.UNKNOWN,
    'REJECTD': MessageState.REJECTED,
    'ENROUTE': MessageState.ENROUTE,
}


def _is_receipt(pdu: tp.Union[DeliverSm, DataSm, SubmitSm]) -> bool:
    # SMSC delivery receipt message type (SMPP v3.4 §5.2.12)
    return (pdu.esm_class & 0x3C) == 0x04


def _tlv(
    pdu: tp.Union[DeliverSm, DataSm, SubmitSm], tag: int
) -> tp.Union[int, str, bytes, None]:
    """get_tlv, treating a malformed TLV as absent."""
    try:
        return pdu.get_tlv(tag)
    except SMPPValidationException:
        return None


def _parse_receipt(pdu: tp.Union[DeliverSm, DataSm, SubmitSm]) -> DeliveryReceipt:
    """Parse a receipt from its Appendix B text, overridden by receipt TLVs."""
    # data_sm has no Appendix B text; its receipt is TLVs only
    fields = pdu.parse_delivery_receipt() if isinstance(pdu, DeliverSm) else {}
    stat = fields.get('stat')
    state = _STAT_TO_STATE.get(stat.upper()) if stat else None
    receipt_id = fields.get('id')

    tlv_id = _tlv(pdu, OptionalTag.RECEIPTED_MESSAGE_ID)
    if isinstance(tlv_id, str):
        receipt_id = tlv_id
    tlv_state = _tlv(pdu, OptionalTag.MESSAGE_STATE)
    if isinstance(tlv_state, int):
        try:
            state = MessageState(tlv_state)
        except ValueError:
            pass

    return DeliveryReceipt(
        id=receipt_id,
        state=state,
        stat=stat,
        err=fields.get('err'),
        submit_date=fields.get('submit_date'),
        done_date=fields.get('done_date'),
        text=fields.get('text'),
    )


def _decode(content: bytes, data_coding: int) -> tp.Optional[str]:
    try:
        return decode_message_with_encoding(content, data_coding)
    except SMPPPDUException:
        return None


def _split(
    pdu: tp.Union[DeliverSm, DataSm, SubmitSm],
) -> tp.Tuple[tp.Optional[ConcatenatedSMSHeader], bytes]:
    """Concat info (from UDH, else SAR TLVs) and the message bytes without UDH."""
    if isinstance(pdu, (DeliverSm, SubmitSm)) and pdu.short_message:
        raw = pdu.short_message
    else:
        raw = pdu.get_optional_parameter_value(OptionalTag.MESSAGE_PAYLOAD) or b''
    if pdu.esm_class & 0x40:  # UDHI
        try:
            udh, offset = UDH.decode(raw)
            raw = raw[offset:]
            element = udh.get_element(UDH.IEI_CONCATENATED_SMS_8BIT) or udh.get_element(
                UDH.IEI_CONCATENATED_SMS_16BIT
            )
            if element:
                return ConcatenatedSMSHeader.from_udh_element(element), raw
        except ValueError:
            pass  # malformed UDH: keep the bytes as they are
    ref = _tlv(pdu, OptionalTag.SAR_MSG_REF_NUM)
    total = _tlv(pdu, OptionalTag.SAR_TOTAL_SEGMENTS)
    seq = _tlv(pdu, OptionalTag.SAR_SEGMENT_SEQNUM)
    if isinstance(ref, int) and isinstance(total, int) and isinstance(seq, int):
        return ConcatenatedSMSHeader(
            reference=ref, total_parts=total, part_number=seq
        ), raw
    return None, raw


def _to_message(
    pdu: tp.Union[DeliverSm, DataSm, SubmitSm], text: tp.Optional[str]
) -> Message:
    return Message(
        sender=Address(pdu.source_addr, pdu.source_addr_ton, pdu.source_addr_npi),
        to=Address(pdu.destination_addr, pdu.dest_addr_ton, pdu.dest_addr_npi),
        text=text,
        receipt=_parse_receipt(pdu)
        if _is_receipt(pdu) and not isinstance(pdu, SubmitSm)
        else None,
        pdu=pdu,
    )
