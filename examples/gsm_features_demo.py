#!/usr/bin/env python3
"""
Demo script showing GSM features usage.

This demonstrates the new GSM 7-bit encoding, message segmentation,
and concatenated SMS support similar to python-smpplib's gsm.make_parts().
"""

import sys
import os

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import smpp.gsm as gsm
from smpp.protocol.pdu.message import SubmitSm


def demo_gsm7_encoding():
    """Demonstrate GSM 7-bit encoding."""
    print('=== GSM 7-bit Encoding Demo ===')

    # Basic GSM 7-bit text
    text = 'Hello World! £¥€'
    encoded, char_count = gsm.encode_gsm7(text)
    decoded = gsm.decode_gsm7(encoded, char_count)

    print(f'Original: {text}')
    print(f'Encoded:  {encoded.hex()}')
    print(f'Chars:    {char_count}')
    print(f'Decoded:  {decoded}')
    print(f'Match:    {text == decoded}')
    print()


def demo_message_segmentation():
    """Demonstrate automatic message segmentation."""
    print('=== Message Segmentation Demo ===')

    # Long message that needs segmentation
    long_message = 'This is a very long SMS message ' * 10  # >160 chars

    print(f'Original message length: {len(long_message)} characters')

    # Split into parts using GSM 7-bit encoding
    parts = gsm.make_parts(long_message, encoding='gsm7')

    print(f'Split into {len(parts)} parts:')
    for i, part in enumerate(parts, 1):
        print(f'  Part {i}/{part.total_parts}:')
        print(f'    Content length: {len(part.content)} bytes')
        print(f'    Has UDH: {part.udh is not None}')
        print(f'    ESM class: 0x{part.get_esm_class():02X}')
        if part.udh:
            concat_info = part.get_concatenated_info()
            if concat_info:
                print(f'    Reference: {concat_info.reference}')
                print(f'    Part: {concat_info.part_number}/{concat_info.total_parts}')
        print()


def demo_udh_handling():
    """Demonstrate UDH creation and parsing."""
    print('=== UDH Handling Demo ===')

    # Create a concatenated SMS header
    concat_header = gsm.ConcatenatedSMSHeader(
        reference=12345, total_parts=3, part_number=1, use_16bit_ref=True
    )

    # Create UDH
    udh = gsm.UDH([concat_header.to_udh_element()])
    udh_bytes = udh.encode()

    print(f'UDH bytes: {udh_bytes.hex()}')
    print(f'UDH length: {len(udh_bytes)} bytes')

    # Parse UDH back
    parsed_udh, offset = gsm.UDH.decode(udh_bytes)
    element = parsed_udh.get_element(gsm.UDH.IEI_CONCATENATED_SMS_16BIT)
    if element is None:
        raise ValueError('Concatenated SMS element not found in UDH')
    parsed_header = gsm.ConcatenatedSMSHeader.from_udh_element(element)

    print(f'Parsed reference: {parsed_header.reference}')
    print(f'Parsed total parts: {parsed_header.total_parts}')
    print(f'Parsed part number: {parsed_header.part_number}')
    print()


def demo_submit_sm_with_udh():
    """Demonstrate SubmitSm PDU with UDH."""
    print('=== SubmitSm with UDH Demo ===')

    # Create message parts
    message = 'Hello from part 1 of 2!'
    parts = gsm.make_parts(message, encoding='gsm7')

    if parts:
        part = parts[0]

        # Create SubmitSm PDU
        pdu = SubmitSm(
            source_addr='1234',
            destination_addr='5678',
            short_message=part.get_short_message(),
            esm_class=part.get_esm_class(),
            data_coding=part.encoding,
        )

        print(f'PDU has UDH: {pdu.has_udh()}')
        print(f'PDU ESM class: 0x{pdu.esm_class:02X}')
        print(f'Short message length: {len(pdu.short_message)} bytes')
        print(f'Message content: {pdu.get_message_content()}')

        # Check concatenated SMS info
        if pdu.is_concatenated_sms():
            concat_info = pdu.get_concatenated_info()
            if concat_info:
                print(f'Concatenated SMS reference: {concat_info.reference}')
                print(f'Part {concat_info.part_number} of {concat_info.total_parts}')
    print()


def demo_compatibility():
    """Demonstrate python-smpplib compatibility."""
    print('=== python-smpplib Compatibility Demo ===')

    # This mimics python-smpplib's usage pattern
    message = 'Привет мир! ' * 10  # Unicode message

    # Split message (similar to smpplib.gsm.make_parts)
    parts = gsm.make_parts(message, encoding='utf16')

    print(f'Unicode message split into {len(parts)} parts')
    print(f'Encoding flag: {parts[0].encoding}')
    print(f'Message type flag: {parts[0].get_esm_class()}')

    # Show the parts would be sent like this:
    for part in parts:
        print(f'Part {part.part_number}: {len(part.content)} bytes')
        # In real usage, you'd send each part as a separate SubmitSm
    print()


if __name__ == '__main__':
    print('GSM Features Demo')
    print('=================')
    print()

    demo_gsm7_encoding()
    demo_message_segmentation()
    demo_udh_handling()
    demo_submit_sm_with_udh()
    demo_compatibility()

    print('Demo completed successfully!')
