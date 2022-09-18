"""Tests to ensure that samples are correct and good for testing.
"""

from .samples import *


def test_bind_transmitter_sample_1_frame():
    p = BindTransmitterPDUSample1()

    expected_frame = (
        b'\x00\x00\x00/\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00'
        b'\x00\x01SMPP3TEST\x00secret08\x00SUBMIT1\x00P\x01\x01\x00'
    )
    assert p.frame == expected_frame


def test_bind_transmitter_sample_1_dict():
    p = BindTransmitterPDUSample1()

    expected_dict = {
        'length': 47,
        'id': 2,
        'status': 0,
        'sequence': 1,
        'sys_id': b'SMPP3TEST',
        'password': b'secret08',
        'sys_type': b'SUBMIT1',
        'iface_version': 0x50,
        'addr_ton': 0x01,
        'addr_npi': 0x01,
        'addr_range': b'',  # 0x00,
    }
    assert p.asdict() == expected_dict


def test_bind_transmitter_sample_2_frame():
    p = BindTransmitterPDUSample2()

    expected_frame = (
        b'\x00\x00\x00\x17\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x01'
        b'\x00\x00\x00P\x01\x01\x00'
    )
    assert p.frame == expected_frame


def test_bind_transmitter_sample_2_dict():
    p = BindTransmitterPDUSample2()

    expected_dict = {
        'length': 23,
        'id': 2,
        'status': 0,
        'sequence': 1,
        'sys_id': b'',
        'password': b'',
        'sys_type': b'',
        'iface_version': 0x50,
        'addr_ton': 0x01,
        'addr_npi': 0x01,
        'addr_range': b'',  # 0x00,
    }
    assert p.asdict() == expected_dict


def test_bind_transmitter_sample_3_frame():
    p = BindTransmitterPDUSample3()

    expected_frame = (
        b'\x00\x00\x00d\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x01SMPP3TEST012'
        b'345\x00PASSWORD1\x00SYSTEMTYPE123\x00P\x01\x01ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ'
        b'ZZZZZZZZZZZ\x00'
    )
    assert p.frame == expected_frame


def test_bind_transmitter_sample_3_dict():
    p = BindTransmitterPDUSample3()

    expected_dict = {
        'length': 100,
        'id': 2,
        'status': 0,
        'sequence': 1,
        'sys_id': b'SMPP3TEST012345',
        'password': b'PASSWORD1',
        'sys_type': b'SYSTEMTYPE123',
        'iface_version': 0x50,
        'addr_ton': 0x01,
        'addr_npi': 0x01,
        'addr_range': b'Z' * 40,
    }
    assert p.asdict() == expected_dict


# vim: sw=4:et:ai
