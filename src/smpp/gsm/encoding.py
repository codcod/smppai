"""
GSM 7-bit encoding implementation for SMS messages.

Provides encoding and decoding functions compatible with python-smpplib's
GSM 7-bit character set handling.
"""

from typing import Optional, Tuple

# GSM 7-bit basic character set
GSM_7BIT_BASIC = (
    '@£$¥èéùìòÇ\nØø\rÅåΔ_ΦΓΛΩΠΨΣΘΞ\x1bÆæßÉ !"#¤%&\'()*+,-./0123456789:;<=>?'
    '¡ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÑÜ§¿abcdefghijklmnopqrstuvwxyzäöñüà'
)

# GSM 7-bit extended character set (escape sequences)
GSM_7BIT_EXTENDED = {
    '\f': 0x0A,  # Form feed
    '^': 0x14,  # Circumflex
    '{': 0x28,  # Left curly bracket
    '}': 0x29,  # Right curly bracket
    '\\': 0x2F,  # Backslash
    '[': 0x3C,  # Left square bracket
    '~': 0x3D,  # Tilde
    ']': 0x3E,  # Right square bracket
    '|': 0x40,  # Vertical bar
    '€': 0x65,  # Euro sign
}

# Reverse mapping for extended characters
GSM_7BIT_EXTENDED_REVERSE = {v: k for k, v in GSM_7BIT_EXTENDED.items()}


def encode_gsm7(text: str) -> Tuple[bytes, int]:
    """
    Encode text to GSM 7-bit format.

    Args:
        text: Unicode text to encode

    Returns:
        Tuple of (encoded_bytes, character_count)

    Raises:
        ValueError: If text contains characters not in GSM 7-bit charset
    """
    if not text:
        return b'', 0

    # First pass: convert to GSM 7-bit values
    gsm_values = []
    char_count = 0

    for char in text:
        if char in GSM_7BIT_BASIC:
            gsm_values.append(GSM_7BIT_BASIC.index(char))
            char_count += 1
        elif char in GSM_7BIT_EXTENDED:
            # Extended character requires escape sequence
            gsm_values.append(0x1B)  # ESC
            gsm_values.append(GSM_7BIT_EXTENDED[char])
            char_count += 2
        else:
            raise ValueError(f'Character {char!r} not supported in GSM 7-bit charset')

    # Pack 7-bit values into bytes
    if not gsm_values:
        return b'', 0

    # Simple bit packing - each character occupies 7 bits
    packed = bytearray()
    accumulator = 0
    bits_in_accumulator = 0

    for value in gsm_values:
        accumulator |= value << bits_in_accumulator
        bits_in_accumulator += 7

        # Extract complete bytes
        while bits_in_accumulator >= 8:
            packed.append(accumulator & 0xFF)
            accumulator >>= 8
            bits_in_accumulator -= 8

    # Add remaining bits if any
    if bits_in_accumulator > 0:
        packed.append(accumulator & 0xFF)

    return bytes(packed), char_count


def decode_gsm7(data: bytes, character_count: Optional[int] = None) -> str:
    """
    Decode GSM 7-bit encoded data to text.

    Args:
        data: GSM 7-bit encoded bytes
        character_count: Number of characters to decode (if None, decode all)

    Returns:
        Decoded Unicode text

    Raises:
        ValueError: If data contains invalid GSM 7-bit values
    """
    if not data:
        return ''

    # Unpack 7-bit values from bytes
    gsm_values = []
    accumulator = 0
    bits_in_accumulator = 0

    for byte_val in data:
        accumulator |= byte_val << bits_in_accumulator
        bits_in_accumulator += 8

        # Extract 7-bit values
        while bits_in_accumulator >= 7:
            gsm_values.append(accumulator & 0x7F)
            accumulator >>= 7
            bits_in_accumulator -= 7

            # Stop if we've reached the character count
            if character_count is not None and len(gsm_values) >= character_count:
                break

        if character_count is not None and len(gsm_values) >= character_count:
            break

    # Convert GSM values to text
    text = []
    i = 0
    while i < len(gsm_values):
        value = gsm_values[i]

        if value == 0x1B and i + 1 < len(gsm_values):
            # Extended character
            next_value = gsm_values[i + 1]
            if next_value in GSM_7BIT_EXTENDED_REVERSE:
                text.append(GSM_7BIT_EXTENDED_REVERSE[next_value])
                i += 2
            else:
                # Invalid escape sequence, treat as space
                text.append(' ')
                i += 1
        elif value < len(GSM_7BIT_BASIC):
            text.append(GSM_7BIT_BASIC[value])
            i += 1
        else:
            # Invalid character, treat as space
            text.append(' ')
            i += 1

    return ''.join(text)
