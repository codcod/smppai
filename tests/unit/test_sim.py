"""Tests for the simulator SMSC (smpp.sim)."""

import asyncio
import urllib.error
import urllib.request

import pytest
import pytest_asyncio

import smpp
from smpp.protocol import RegisteredDelivery
from smpp.sim import Simulator, _parser


def make_sim(*stats):
    return Simulator(
        '127.0.0.1',
        0,
        http_port=0,
        receipt_delay=0.05,
        stats=stats or (('DELIVRD', 1),),
        setup_signal_handlers=False,
    )


@pytest_asyncio.fixture
async def sim(request):
    s = make_sim(*getattr(request, 'param', ()))
    await s.start()
    yield s
    await s.stop()


async def next_message(client, timeout=1.0):
    async def first():
        async for m in client.messages():
            return m

    return await asyncio.wait_for(first(), timeout)


async def no_message(client, timeout=0.3):
    with pytest.raises(asyncio.TimeoutError):
        await next_message(client, timeout)


def post(port, query):
    req = urllib.request.Request(f'http://127.0.0.1:{port}/mo?{query}', method='POST')
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:  # nosec B310
            return resp.status
    except urllib.error.HTTPError as e:
        return e.code


@pytest.mark.asyncio
class TestReceipts:
    async def test_receipt_carries_the_submit_id(self, sim):
        async with smpp.connect('127.0.0.1', sim.port, 'u', 'p') as c:
            result = await c.send('+306900000001', 'hello', receipt=True)
            msg = await next_message(c)
        assert msg.receipt.id == result.message_ids[0]
        assert msg.receipt.stat == 'DELIVRD'
        assert msg.receipt.text == 'hello'

    async def test_no_receipt_when_not_asked(self, sim):
        async with smpp.connect('127.0.0.1', sim.port, 'u', 'p') as c:
            await c.send('+306900000001', 'hello')
            await no_message(c)

    @pytest.mark.parametrize(
        'sim, wanted',
        [((('DELIVRD', 1),), False), ((('UNDELIV', 1),), True)],
        indirect=['sim'],
    )
    async def test_failure_only_receipt(self, sim, wanted):
        async with smpp.connect('127.0.0.1', sim.port, 'u', 'p') as c:
            await c.raw.submit_sm(
                '',
                '306900000001',
                'hi',
                registered_delivery=RegisteredDelivery.FAILURE_ONLY,
            )
            if wanted:
                assert (await next_message(c)).receipt.stat == 'UNDELIV'
            else:
                await no_message(c)

    async def test_throttled_receipt_is_resent(self, sim, monkeypatch):
        from smpp import sim as sim_module
        from smpp.client import highlevel

        monkeypatch.setattr(highlevel, '_MAX_PENDING', 1)
        monkeypatch.setattr(sim_module, '_RECEIPT_RETRY', 0.05)
        async with smpp.connect('127.0.0.1', sim.port, 'u', 'p') as c:
            sent = [
                await c.send('+306900000001', f'm{i}', receipt=True) for i in range(3)
            ]
            await asyncio.sleep(0.2)  # receipts 2 and 3 meet a full queue
            got = []

            async def three():
                async for m in c.messages():
                    got.append(m.receipt.id)
                    if len(got) == 3:
                        return

            await asyncio.wait_for(three(), 2)
        assert sorted(got) == sorted(r.message_ids[0] for r in sent)

    @pytest.mark.parametrize('sim', [(('NONE', 1),)], indirect=True)
    async def test_stat_none_sends_no_receipt(self, sim):
        async with smpp.connect('127.0.0.1', sim.port, 'u', 'p') as c:
            await c.send('+306900000001', 'hello', receipt=True)
            await no_message(c)


@pytest.mark.asyncio
class TestMO:
    async def test_mo(self, sim):
        async with smpp.connect('127.0.0.1', sim.port, 'u', 'p') as c:
            assert await sim.mo('+306900000001', '1234', 'hi')
            msg = await next_message(c)
        assert msg.text == 'hi'
        assert msg.sender.addr == '306900000001'
        assert msg.receipt is None

    async def test_mo_over_http(self, sim):
        async with smpp.connect('127.0.0.1', sim.port, 'u', 'p') as c:
            status = await asyncio.to_thread(
                post,
                sim.http_port,
                'from=%2B306900000001&to=1234&text=%CE%93%CE%B5%CE%B9%CE%AC',
            )
            msg = await next_message(c)
            missing = await asyncio.to_thread(post, sim.http_port, 'from=1&to=2')
        assert status == 200
        assert msg.text == 'Γειά'
        assert missing == 400

    async def test_mo_over_http_without_receiver(self, sim):
        status = await asyncio.to_thread(post, sim.http_port, 'from=1&to=2&text=hi')
        assert status == 409


def test_stat_parsing():
    args = _parser().parse_args(['--stat', 'DELIVRD:9', '--stat', 'undeliv'])
    assert args.stat == [('DELIVRD', 9), ('UNDELIV', 1)]


@pytest.mark.parametrize('bad', ['BOGUS', 'DELIVRD:0', 'DELIVRD:x'])
def test_bad_stat_exits_2(bad):
    with pytest.raises(SystemExit) as e:
        _parser().parse_args(['--stat', bad])
    assert e.value.code == 2
