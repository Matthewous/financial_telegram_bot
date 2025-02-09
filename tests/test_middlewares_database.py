# tests/test_middlewares_database.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from middlewares.database import DataBaseSession
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.mark.asyncio
async def test_database_session_middleware(async_engine):
    # Create a mock session pool
    mock_session_pool = AsyncMock()

    # Create a mock handler
    mock_handler = AsyncMock()

    # Create a mock event
    mock_event = MagicMock()

    # Create a mock data dictionary
    mock_data = {}

    # Create an instance of the middleware
    middleware = DataBaseSession(session_pool=mock_session_pool)

    # Call the middleware
    await middleware(handler=mock_handler, event=mock_event, data=mock_data)

    # Assert that the session was added to the data dictionary
    assert "session" in mock_data
    assert isinstance(mock_data["session"], AsyncSession)

    # Assert that the handler was called with the event and data
    mock_handler.assert_called_once_with(mock_event, mock_data)

    # Clean up
    await async_engine.dispose()