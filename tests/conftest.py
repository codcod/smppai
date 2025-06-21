"""
Shared test fixtures and configuration for SMPP unit tests.
"""

import asyncio
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_asyncio_sleep():
    """Mock asyncio.sleep to speed up tests."""

    async def fast_sleep(duration):
        # Sleep for a very short time instead of the full duration
        await asyncio.sleep(0.001)

    return fast_sleep


@pytest.fixture
def mock_time():
    """Mock time.time() for consistent timestamps in tests."""
    return MagicMock(return_value=1000000.0)


@pytest.fixture
def mock_logger():
    """Mock logger for testing log output."""
    return MagicMock()


# Common test data
@pytest.fixture
def sample_pdu_data():
    """Sample PDU data for testing."""
    return {
        'sequence_number': 12345,
        'command_id': 0x80000001,
        'command_status': 0,
        'length': 16,
    }


@pytest.fixture
def sample_host_port():
    """Sample host and port for testing."""
    return {'host': 'localhost', 'port': 2775}
