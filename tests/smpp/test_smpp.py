from smppai.smpp import pack, unpack, BindTransmitter
from .samples import *


def test_unpack():
    samples = [
        (BindTransmitterPDUSample1(), BindTransmitter),
        (BindTransmitterPDUSample2(), BindTransmitter),
        (BindTransmitterPDUSample3(), BindTransmitter),
    ]
    for sample, klass in samples:
        f = sample.frame
        pdu = unpack(f)
        assert type(pdu) == klass


def test_pack():
    samples = [
        (BindTransmitterPDUSample1(), BindTransmitter),
        (BindTransmitterPDUSample2(), BindTransmitter),
        (BindTransmitterPDUSample3(), BindTransmitter),
    ]
    for sample, klass in samples:
        f = pack(sample)
        assert f == sample.frame


def test_bind_transmitter_load():
    samples = [
        BindTransmitterPDUSample1(),
        BindTransmitterPDUSample2(),
        BindTransmitterPDUSample3(),
    ]
    for sample in samples:
        p = BindTransmitter()
        p.load(sample.frame)
        assert p.__dict__ == sample.asdict()


# vim: sw=4:et:ai
