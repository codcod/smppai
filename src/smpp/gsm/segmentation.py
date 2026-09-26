"""
Message segmentation for SMS messages.

Provides automatic message splitting for long SMS messages with
concatenated SMS support.
"""

import random
from dataclasses import dataclass
import typing as tp

from ..exceptions import SMPPPDUException
from .constants import (
    EIGHTBIT_LENGTH,
    EIGHTBIT_PART_SIZE,
    SEVENBIT_LENGTH,
    SEVENBIT_PART_SIZE,
)
from .udh import UDH, ConcatenatedSMSHeader


@dataclass
class MessagePart:
    """
    A single part of a segmented SMS message.

    Attributes:
        content: Message content as bytes
        udh: User Data Header (if any)
        encoding: Data coding scheme
        part_number: Part number in sequence (1-based)
        total_parts: Total number of parts
        reference: Message reference for concatenation
    """

    content: bytes
    udh: tp.Optional[UDH] = None
    encoding: int = 0  # GSM 7-bit default
    part_number: int = 1
    total_parts: int = 1
    reference: tp.Optional[int] = None

    def get_short_message(self) -> bytes:
        """
        Get the complete short message including UDH.

        Returns:
            Complete message bytes for SMPP short_message field
        """
        if self.udh:
            udh_bytes = self.udh.encode()
            return udh_bytes + self.content
        return self.content

    def get_esm_class(self, base_esm_class: int = 0) -> int:
        """
        Get ESM class with UDH indicator if needed.

        Args:
            base_esm_class: Base ESM class value

        Returns:
            ESM class with UDH indicator set if UDH present
        """
        if self.udh:
            return base_esm_class | 0x40  # Set UDH indicator
        return base_esm_class

    def get_concatenated_info(self) -> tp.Optional[ConcatenatedSMSHeader]:
        """
        Get concatenated SMS information if this part has UDH.

        Returns:
            ConcatenatedSMSHeader if this is part of concatenated SMS, None otherwise
        """
        if not self.udh:
            return None

        # Try 8-bit reference first
        element = self.udh.get_element(UDH.IEI_CONCATENATED_SMS_8BIT)
        if element:
            return ConcatenatedSMSHeader.from_udh_element(element)

        # Try 16-bit reference
        element = self.udh.get_element(UDH.IEI_CONCATENATED_SMS_16BIT)
        if element:
            return ConcatenatedSMSHeader.from_udh_element(element)

        return None


def make_parts(
    message: tp.Union[str, bytes],
    data_coding: int = 0,  # smpp.protocol.constants.DataCoding.DEFAULT
    reference: tp.Optional[int] = None,
) -> tp.List[MessagePart]:
    """
    Split a message into SMS parts for transmission.

    Each part is encoded through smpp.protocol.codec, so data_coding governs
    the bytes on the wire the same way submit_sm's data_coding does. Text is
    never split inside a character: a GSM escape pair or a UCS2 surrogate
    pair (a non-BMP character) always stays in one part.

    Args:
        message: Message text, or pre-encoded bytes (sliced at the octet
            budget as-is, not re-encoded; any data_coding is accepted)
        data_coding: SMPP data_coding value the parts are encoded/labeled with
        reference: 0-255 concatenation reference (random if None)

    Returns:
        List of MessagePart objects in part_number order. A message that
        fits one segment returns a single part with udh=None.

    Raises:
        ValueError: If reference is out of range, or the message needs more
            than 255 parts
        SMPPPDUException: If message can't be encoded with data_coding
    """
    # protocol.codec imports smpp.gsm at module level to register the
    # 'gsm0338' codec, so a module-level import back here would cycle.
    from ..protocol.codec import codec_for_data_coding, encode_message_with_encoding

    if reference is not None and not 0 <= reference <= 255:
        raise ValueError(f'reference must be 0-255, got {reference}')

    try:
        codec = codec_for_data_coding(data_coding)
    except SMPPPDUException:
        # Raw-only coding (JIS, pictogram, ...): bytes still slice; text
        # fails in encode_message_with_encoding below.
        codec = None
    is_gsm = codec == 'gsm0338'
    single_budget = SEVENBIT_LENGTH if is_gsm else EIGHTBIT_LENGTH
    part_budget = SEVENBIT_PART_SIZE if is_gsm else EIGHTBIT_PART_SIZE

    if isinstance(message, bytes):
        chunks = (
            [message]
            if len(message) <= single_budget
            else [
                message[i : i + part_budget]
                for i in range(0, len(message), part_budget)
            ]
        )
    else:
        encoded = encode_message_with_encoding(message, data_coding)
        chunks = (
            [encoded]
            if len(encoded) <= single_budget
            else _split_by_character(
                message, data_coding, part_budget, codec in _STATEFUL_CODECS
            )
        )

    if len(chunks) > 255:
        raise ValueError('Message too long for concatenated SMS')

    if len(chunks) == 1:
        return [
            MessagePart(
                content=chunks[0], encoding=data_coding, part_number=1, total_parts=1
            )
        ]

    if reference is None:
        reference = random.randrange(256)

    total_parts = len(chunks)
    parts = []
    for part_number, chunk in enumerate(chunks, start=1):
        header = ConcatenatedSMSHeader(
            reference=reference, total_parts=total_parts, part_number=part_number
        )
        parts.append(
            MessagePart(
                content=chunk,
                udh=UDH([header.to_udh_element()]),
                encoding=data_coding,
                part_number=part_number,
                total_parts=total_parts,
                reference=reference,
            )
        )
    return parts


# Codecs whose per-character encodes don't concatenate to the whole-string
# encode (escape-sequence state), so parts must be encoded as runs.
_STATEFUL_CODECS = frozenset({'iso2022_jp'})


def _split_by_character(
    text: str, data_coding: int, part_budget: int, stateful: bool = False
) -> tp.List[bytes]:
    """
    Greedily pack encoded characters into parts, never splitting one.

    Stateful codecs are packed by run: each part is the whole-string encode
    of its characters, so it carries its own escape sequences and decodes
    on its own.
    """
    from ..protocol.codec import encode_message_with_encoding

    if stateful:
        # ponytail: O(n·part) re-encode, only for stateful codecs; incremental
        # encoder if a large stateful coding is ever added
        runs: tp.List[bytes] = []
        run = ''
        for ch in text:
            if (
                run
                and len(encode_message_with_encoding(run + ch, data_coding))
                > part_budget
            ):
                runs.append(encode_message_with_encoding(run, data_coding))
                run = ''
            run += ch
        if run:
            runs.append(encode_message_with_encoding(run, data_coding))
        return runs

    chunks: tp.List[bytes] = []
    current = bytearray()
    for ch in text:
        ch_bytes = encode_message_with_encoding(ch, data_coding)
        if current and len(current) + len(ch_bytes) > part_budget:
            chunks.append(bytes(current))
            current = bytearray()
        current.extend(ch_bytes)
    if current:
        chunks.append(bytes(current))
    return chunks


def reassemble_parts(parts: tp.List[MessagePart], data_coding: int = 0) -> str:
    """
    Reassemble message parts into the original text.

    For raw-bytes callers, joining `part.content` in `part_number` order is
    trivial and needs no helper.

    Args:
        parts: MessagePart objects to reassemble (any order)
        data_coding: SMPP data_coding the parts were encoded with

    Returns:
        The original message text

    Raises:
        ValueError: If parts are incomplete or inconsistent
        SMPPPDUException: If the joined bytes can't be decoded with data_coding
    """
    from ..protocol.codec import decode_message_with_encoding

    if not parts:
        return ''

    sorted_parts = sorted(parts, key=lambda p: p.part_number)

    total_parts = sorted_parts[0].total_parts
    if len(sorted_parts) != total_parts:
        raise ValueError(f'Incomplete message: {len(sorted_parts)}/{total_parts} parts')

    for i, part in enumerate(sorted_parts, 1):
        if part.part_number != i:
            raise ValueError(f'Missing part {i}')
        if part.total_parts != total_parts:
            raise ValueError('Inconsistent total_parts across message parts')

    return decode_message_with_encoding(
        b''.join(part.content for part in sorted_parts), data_coding
    )
