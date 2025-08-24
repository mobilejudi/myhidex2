import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_event_bus(mocker):
    """Mocks the event bus."""
    mock_bus = MagicMock()
    mock_bus.publish = AsyncMock()
    mocker.patch("bus.events.bus", mock_bus)
    return mock_bus
