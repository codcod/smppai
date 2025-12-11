"""
Message segmentation for SMS messages.

Provides automatic message splitting for long SMS messages with
concatenated SMS support.
"""

import time
from dataclasses import dataclass
from typing import List, Optional, Union

from .encoding import encode_gsm7, decode_gsm7
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
    udh: Optional[UDH] = None
    encoding: int = 0  # GSM 7-bit default
    part_number: int = 1
    total_parts: int = 1
    reference: Optional[int] = None

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

    def get_concatenated_info(self) -> Optional[ConcatenatedSMSHeader]:
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
    message: Union[str, bytes],
    encoding: str = 'gsm7',
    max_sms_length: Optional[int] = None,
    reference: Optional[int] = None
) -> List[MessagePart]:
    """
    Split a message into SMS parts for transmission.

    Args:
        message: Message text or bytes to split
        encoding: Encoding to use ('gsm7', 'latin1', 'utf8', 'utf16')
        max_sms_length: Maximum length per SMS (auto-detected if None)
        reference: Message reference for concatenation (auto-generated if None)

    Returns:
        List of MessagePart objects

    Raises:
        ValueError: If encoding is unsupported or message cannot be encoded
    """
    if isinstance(message, str):
        if encoding == 'gsm7':
            encoded_data, char_count = encode_gsm7(message)
            data_coding = 0
        elif encoding == 'latin1':
            encoded_data = message.encode('latin1')
            data_coding = 3
        elif encoding == 'utf8':
            encoded_data = message.encode('utf-8')
            data_coding = 8
        elif encoding == 'utf16':
            # UTF-16 BE with BOM
            encoded_data = b'\xfe\xff' + message.encode('utf-16be')
            data_coding = 8
        else:
            raise ValueError(f'Unsupported encoding: {encoding}')
    else:
        # Already bytes
        encoded_data = message
        data_coding = 0  # Assume GSM 7-bit
        char_count = len(encoded_data)

    # Determine maximum length per part
    if max_sms_length is None:
        if encoding == 'gsm7':
            max_single = 160  # characters
            max_concat = 153   # characters per part with UDH
        else:
            max_single = 140  # bytes
            max_concat = 134  # bytes per part with UDH
    else:
        max_single = max_sms_length
        max_concat = max_sms_length - 7  # Reserve space for UDH

    # Check if message fits in single SMS
    message_length = len(encoded_data) if encoding != 'gsm7' else char_count

    if message_length <= max_single:
        # Single SMS
        return [MessagePart(
            content=encoded_data,
            encoding=data_coding,
            part_number=1,
            total_parts=1
        )]

    # Multi-part SMS required
    if reference is None:
        reference = int(time.time()) % 65536  # 16-bit reference

    # Calculate number of parts needed
    if encoding == 'gsm7':
        # For GSM 7-bit, we need to re-encode each part
        parts_needed = (char_count + max_concat - 1) // max_concat
        use_16bit_ref = reference > 255 or parts_needed > 255

        # Adjust max length if using 16-bit reference (longer UDH)
        if use_16bit_ref:
            max_concat -= 1  # 16-bit UDH is 1 byte longer
            parts_needed = (char_count + max_concat - 1) // max_concat

        if parts_needed > 255:
            raise ValueError('Message too long for concatenated SMS')

        # Split the original text and re-encode each part
        parts = []
        text = message if isinstance(message, str) else decode_gsm7(encoded_data)

        char_offset = 0
        for part_num in range(1, parts_needed + 1):
            # Extract characters for this part
            part_text = text[char_offset:char_offset + max_concat]
            part_data, _ = encode_gsm7(part_text)
            char_offset += len(part_text)

            # Create UDH
            concat_header = ConcatenatedSMSHeader(
                reference=reference,
                total_parts=parts_needed,
                part_number=part_num,
                use_16bit_ref=use_16bit_ref
            )
            udh = UDH([concat_header.to_udh_element()])

            parts.append(MessagePart(
                content=part_data,
                udh=udh,
                encoding=data_coding,
                part_number=part_num,
                total_parts=parts_needed,
                reference=reference
            ))
    else:
        # For binary encodings, split by bytes
        parts_needed = (len(encoded_data) + max_concat - 1) // max_concat
        use_16bit_ref = reference > 255 or parts_needed > 255

        if use_16bit_ref:
            max_concat -= 1
            parts_needed = (len(encoded_data) + max_concat - 1) // max_concat

        if parts_needed > 255:
            raise ValueError('Message too long for concatenated SMS')

        parts = []
        byte_offset = 0

        for part_num in range(1, parts_needed + 1):
            # Extract bytes for this part
            part_data = encoded_data[byte_offset:byte_offset + max_concat]
            byte_offset += len(part_data)

            # Create UDH
            concat_header = ConcatenatedSMSHeader(
                reference=reference,
                total_parts=parts_needed,
                part_number=part_num,
                use_16bit_ref=use_16bit_ref
            )
            udh = UDH([concat_header.to_udh_element()])

            parts.append(MessagePart(
                content=part_data,
                udh=udh,
                encoding=data_coding,
                part_number=part_num,
                total_parts=parts_needed,
                reference=reference
            ))

    return parts


def reassemble_parts(parts: List[MessagePart], encoding: str = 'gsm7') -> Union[str, bytes]:
    """
    Reassemble message parts into original message.

    Args:
        parts: List of MessagePart objects to reassemble
        encoding: Original encoding used

    Returns:
        Reassembled message (str for text encodings, bytes for binary)

    Raises:
        ValueError: If parts are invalid or incomplete
    """
    if not parts:
        return '' if encoding in ('gsm7', 'latin1', 'utf8', 'utf16') else b''

    if len(parts) == 1 and not parts[0].udh:
        # Single part message
        if encoding == 'gsm7':
            return decode_gsm7(parts[0].content)
        elif encoding in ('latin1', 'utf8', 'utf16'):
            return parts[0].content.decode(encoding.replace('utf16', 'utf-16'))
        else:
            return parts[0].content

    # Sort parts by part number
    sorted_parts = sorted(parts, key=lambda p: p.part_number)

    # Validate completeness
    total_parts = sorted_parts[0].total_parts
    if len(sorted_parts) != total_parts:
        raise ValueError(f'Incomplete message: {len(sorted_parts)}/{total_parts} parts')

    for i, part in enumerate(sorted_parts, 1):
        if part.part_number != i:
            raise ValueError(f'Missing part {i}')
        if part.total_parts != total_parts:
            raise ValueError('Inconsistent total_parts across message parts')

    # Reassemble content
    if encoding == 'gsm7':
        # Decode each part and concatenate text
        text_parts = [decode_gsm7(part.content) for part in sorted_parts]
        return ''.join(text_parts)
    elif encoding in ('latin1', 'utf8', 'utf16'):
        # Concatenate bytes and decode
        all_bytes = b''.join(part.content for part in sorted_parts)
        return all_bytes.decode(encoding.replace('utf16', 'utf-16'))
    else:
        # Binary data
        return b''.join(part.content for part in sorted_parts)
