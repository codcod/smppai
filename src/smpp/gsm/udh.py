"""
User Data Header (UDH) implementation for SMS messages.

Provides UDH parsing and generation for concatenated SMS and other features.
"""

from dataclasses import dataclass
import typing as tp


@dataclass
class UDHElement:
    """
    User Data Header element.

    Attributes:
        iei: Information Element Identifier
        data: Element data bytes
    """

    iei: int
    data: bytes

    def encode(self) -> bytes:
        """Encode UDH element to bytes."""
        return bytes([self.iei, len(self.data)]) + self.data

    @classmethod
    def decode(cls, data: bytes, offset: int = 0) -> tuple['UDHElement', int]:
        """Decode UDH element from bytes."""
        if len(data) - offset < 2:
            raise ValueError('Insufficient data for UDH element header')

        iei = data[offset]
        length = data[offset + 1]

        if len(data) - offset < 2 + length:
            raise ValueError('Insufficient data for UDH element data')

        element_data = data[offset + 2 : offset + 2 + length]
        return cls(iei, element_data), offset + 2 + length


class UDH:
    """
    User Data Header for SMS messages.

    Handles parsing and generation of UDH for concatenated SMS and other features.
    """

    # Information Element Identifiers
    IEI_CONCATENATED_SMS_8BIT = 0x00
    IEI_CONCATENATED_SMS_16BIT = 0x08
    IEI_APPLICATION_PORT_8BIT = 0x04
    IEI_APPLICATION_PORT_16BIT = 0x05

    def __init__(self, elements: tp.Optional[tp.List[UDHElement]] = None):
        """Initialize UDH with optional elements."""
        self.elements = elements or []

    def add_element(self, iei: int, data: bytes) -> None:
        """Add UDH element."""
        self.elements.append(UDHElement(iei, data))

    def get_element(self, iei: int) -> tp.Optional[UDHElement]:
        """Get UDH element by IEI."""
        for element in self.elements:
            if element.iei == iei:
                return element
        return None

    def encode(self) -> bytes:
        """
        Encode UDH to bytes.

        Returns:
            UDH bytes including length header
        """
        if not self.elements:
            return b''

        # Encode all elements
        element_data = b''.join(element.encode() for element in self.elements)

        # Add UDH length header
        udh_length = len(element_data)
        return bytes([udh_length]) + element_data

    @classmethod
    def decode(cls, data: bytes, offset: int = 0) -> tuple['UDH', int]:
        """
        Decode UDH from bytes.

        Args:
            data: Bytes to decode from
            offset: Starting offset

        Returns:
            Tuple of (UDH instance, new offset)
        """
        if len(data) - offset < 1:
            raise ValueError('Insufficient data for UDH length')

        udh_length = data[offset]
        if len(data) - offset < 1 + udh_length:
            raise ValueError('Insufficient data for UDH content')

        elements = []
        element_offset = offset + 1
        end_offset = offset + 1 + udh_length

        while element_offset < end_offset:
            element, element_offset = UDHElement.decode(data, element_offset)
            elements.append(element)

        return cls(elements), offset + 1 + udh_length

    def get_length(self) -> int:
        """Get total UDH length including length header."""
        if not self.elements:
            return 0
        return 1 + sum(2 + len(element.data) for element in self.elements)


@dataclass
class ConcatenatedSMSHeader:
    """
    Concatenated SMS header information.

    Attributes:
        reference: Message reference (8 or 16-bit)
        total_parts: Total number of parts
        part_number: Current part number (1-based)
        use_16bit_ref: Whether to use 16-bit reference
    """

    reference: int
    total_parts: int
    part_number: int
    use_16bit_ref: bool = False

    def to_udh_element(self) -> UDHElement:
        """Convert to UDH element."""
        if self.use_16bit_ref:
            # 16-bit reference
            data = bytes(
                [
                    (self.reference >> 8) & 0xFF,
                    self.reference & 0xFF,
                    self.total_parts,
                    self.part_number,
                ]
            )
            return UDHElement(UDH.IEI_CONCATENATED_SMS_16BIT, data)
        else:
            # 8-bit reference
            data = bytes([self.reference & 0xFF, self.total_parts, self.part_number])
            return UDHElement(UDH.IEI_CONCATENATED_SMS_8BIT, data)

    @classmethod
    def from_udh_element(cls, element: UDHElement) -> 'ConcatenatedSMSHeader':
        """Create from UDH element."""
        if element.iei == UDH.IEI_CONCATENATED_SMS_8BIT:
            if len(element.data) != 3:
                raise ValueError('Invalid 8-bit concatenated SMS UDH data length')
            return cls(
                reference=element.data[0],
                total_parts=element.data[1],
                part_number=element.data[2],
                use_16bit_ref=False,
            )
        elif element.iei == UDH.IEI_CONCATENATED_SMS_16BIT:
            if len(element.data) != 4:
                raise ValueError('Invalid 16-bit concatenated SMS UDH data length')
            return cls(
                reference=(element.data[0] << 8) | element.data[1],
                total_parts=element.data[2],
                part_number=element.data[3],
                use_16bit_ref=True,
            )
        else:
            raise ValueError(f'Invalid concatenated SMS IEI: 0x{element.iei:02X}')
