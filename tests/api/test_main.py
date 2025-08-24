import pytest
import pytest_asyncio
from httpx import AsyncClient
from api.main import app, get_db_session
from unittest.mock import MagicMock, AsyncMock

# Mark all tests in this file as asyncio
pytestmark = pytest.mark.asyncio

@pytest_asyncio.fixture
async def client():
    """Create an async test client for the app."""
    # To prevent the real DB connection on startup
    app.dependency_overrides[get_db_session] = lambda: None
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides = {} # Clean up

@pytest_asyncio.fixture
def mock_db_session():
    """Fixture to override the DB session dependency with a mock."""
    mock_session = AsyncMock()

    # This mock will be injected by the dependency override
    async def override_get_db():
        yield mock_session

    app.dependency_overrides[get_db_session] = override_get_db
    yield mock_session
    # Clean up
    del app.dependency_overrides[get_db_session]


async def test_health_check(client: AsyncClient):
    """Tests the /health endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"ok": True}

async def test_list_signals_empty(client: AsyncClient, mock_db_session: AsyncMock):
    """Tests the /signals endpoint when there are no signals."""
    mock_result = MagicMock()
    mock_result.mappings.return_value.all.return_value = []
    mock_db_session.execute.return_value = mock_result

    response = await client.get("/signals")
    assert response.status_code == 200
    assert response.json() == []
    mock_db_session.execute.assert_awaited_once()

async def test_list_signals_with_data(client: AsyncClient, mock_db_session: AsyncMock):
    """Tests the /signals endpoint with some mock data."""
    # The result of .all() is a list of mapping-like objects (e.g., dicts)
    mock_data = [
        {"id": 1, "score": 2.5},
        {"id": 2, "score": 1.8},
    ]

    mock_result = MagicMock()
    mock_result.mappings.return_value.all.return_value = mock_data
    mock_db_session.execute.return_value = mock_result

    response = await client.get("/signals")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data == mock_data

async def test_websocket_endpoint():
    """Tests the /ws WebSocket endpoint connection."""
    from api.main import ws_endpoint, subscribers

    subscribers.clear()

    mock_websocket = AsyncMock()
    mock_websocket.accept = AsyncMock()
    mock_websocket.receive_text = AsyncMock(side_effect=Exception("Simulating disconnect"))

    with pytest.raises(Exception, match="Simulating disconnect"):
        await ws_endpoint(mock_websocket)

    mock_websocket.accept.assert_awaited_once()
    assert len(subscribers) == 1

    subscribers.clear()
