"""
Integration test against the opensmpp simulator (local only)

Runs when the opensmpp simulator answers a bind on localhost:2775
(`docker compose up -d` in the opensmpp repo) and skips otherwise, so CI and a
local smppai example server on the same port stay green. It checks submit_sm/deliver_sm field order against a third-party SMSC,
which our own client/server pair cannot: they share one codec.
"""

import asyncio
import socket

import pytest

from smpp import DataCoding, RegisteredDelivery, SMPPClient
from smpp.protocol import BindTransceiver

SIM_HOST = 'localhost'
SIM_PORT = 2775


def _is_opensmpp_sim() -> bool:
    """Bind once and look for the simulator's bind_resp system_id."""
    bind = BindTransceiver(
        system_id='smppclient1', password='password', sequence_number=1
    )
    try:
        with socket.create_connection((SIM_HOST, SIM_PORT), timeout=1) as sock:
            sock.sendall(bind.encode())
            return b'Smsc Simulator' in sock.recv(1024)
    except OSError:
        return False


@pytest.fixture(scope='module', autouse=True)
def _require_sim():
    # A fixture, not an import-time check, so unrelated runs never probe.
    if not _is_opensmpp_sim():
        pytest.skip('opensmpp simulator not reachable on localhost:2775')


@pytest.mark.integration
@pytest.mark.asyncio
async def test_submit_with_receipt_and_receive_dlr():
    receipts = []

    # Credentials from the simulator's sim/users.txt
    async with SMPPClient(SIM_HOST, SIM_PORT, 'smppclient1', 'password') as client:
        client.on_deliver_sm = lambda _client, pdu: receipts.append(pdu)
        await client.bind_transceiver()

        ids = [
            await client.submit_sm(
                '12345',
                '67890',
                'Hello from smppai',
                registered_delivery=RegisteredDelivery.SUCCESS_FAILURE,
            ),
            await client.submit_sm(
                '12345',
                '67890',
                'Γειά σου κόσμε',
                registered_delivery=RegisteredDelivery.SUCCESS_FAILURE,
                data_coding=DataCoding.UCS2,
            ),
        ]
        assert all(ids)

        # The simulator flushes its receipt queue every 5 s.
        # Stray deliver_sm (earlier runs' receipts, MOs) must not end the wait.
        def ours():
            return {
                m: p
                for p in receipts
                for m in ids
                if p.get_message_text().startswith(f'id:{m} ')
            }

        for _ in range(150):
            if len(ours()) == len(ids):
                break
            await asyncio.sleep(0.1)

    matched = ours()
    assert set(matched) == set(ids), [p.get_message_text() for p in receipts]
    for pdu in matched.values():
        assert pdu.esm_class & 0x04
        assert pdu.data_coding == 3
