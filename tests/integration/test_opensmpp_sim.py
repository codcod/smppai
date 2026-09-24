"""
Integration test against the opensmpp simulator (local only)

Runs when something accepts TCP on localhost:2775 (the opensmpp simulator,
`docker compose up -d` in the opensmpp repo) and skips otherwise, so CI stays
green. It checks submit_sm/deliver_sm field order against a third-party SMSC,
which our own client/server pair cannot: they share one codec.
"""

import asyncio
import socket

import pytest

from smpp import DataCoding, RegisteredDelivery, SMPPClient

SIM_HOST = 'localhost'
SIM_PORT = 2775


def _sim_reachable() -> bool:
    try:
        socket.create_connection((SIM_HOST, SIM_PORT), timeout=1).close()
        return True
    except OSError:
        return False


if not _sim_reachable():
    pytest.skip(
        'opensmpp simulator not reachable on localhost:2775', allow_module_level=True
    )


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
        for _ in range(150):
            if len(receipts) >= 2:
                break
            await asyncio.sleep(0.1)

    assert len(receipts) >= 2
    texts = [pdu.get_message_text() for pdu in receipts]
    for pdu in receipts:
        assert pdu.esm_class & 0x04
        assert pdu.data_coding == 3
    for message_id in ids:
        assert any(t.startswith(f'id:{message_id}') for t in texts), (message_id, texts)
