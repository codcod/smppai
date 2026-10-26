"""Unit tests for smpp.utils helpers."""

import logging
import time

import pytest

from smpp import utils


def test_generate_message_id_is_numeric_and_in_range():
    message_id = utils.generate_message_id()
    assert message_id.isdigit()
    assert 0 <= int(message_id) < 0x7FFFFFFF


def test_normalize_phone_number():
    assert utils.normalize_phone_number('+1 (555) 010-9999') == '15550109999'


@pytest.mark.parametrize(
    'phone,valid',
    [
        ('123456', False),
        ('1234567', True),
        ('+44 20 7946 0958', True),
        ('1' * 16, False),
    ],
)
def test_validate_phone_number(phone, valid):
    assert utils.validate_phone_number(phone) is valid


@pytest.mark.parametrize(
    'system_id,valid',
    [('', False), ('esme', True), ('x' * 15, True), ('x' * 16, False)],
)
def test_is_valid_system_id(system_id, valid):
    assert utils.is_valid_system_id(system_id) is valid


@pytest.mark.parametrize(
    'text,field,expected',
    [
        ('secret', 'password', '******'),
        ('a-very-long-secret', 'Password', '********'),
        ('', 'password', ''),
        ('esme', 'system_id', 'esme'),
    ],
)
def test_mask_sensitive_data(text, field, expected):
    assert utils.mask_sensitive_data(text, field) == expected


def test_setup_logging(monkeypatch):
    calls = []
    monkeypatch.setattr(logging, 'basicConfig', lambda **kw: calls.append(kw))
    utils.setup_logging(logging.DEBUG)
    assert calls[0]['level'] == logging.DEBUG


@pytest.mark.parametrize('message,length', [('héllo', 6), (b'\x00\x01', 2)])
def test_calculate_message_length(message, length):
    assert utils.calculate_message_length(message) == length


def test_format_smpp_time():
    assert utils.format_smpp_time(0) == '700101000000000+'
    assert len(utils.format_smpp_time()) == 16


@pytest.mark.parametrize('value', ['', '2401020304', '24ab02030405000+'])
def test_parse_smpp_time_rejects(value):
    assert utils.parse_smpp_time(value) is None


def test_parse_smpp_time():
    # parse uses local time (mktime) while format uses UTC (gmtime), so
    # compare against mktime rather than round-tripping.
    expected = time.mktime(time.strptime('20240102030405', '%Y%m%d%H%M%S'))
    assert utils.parse_smpp_time('240102030405000+') == expected
