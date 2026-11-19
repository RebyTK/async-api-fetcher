
from unittest.mock import AsyncMock, Mock, patch

import pytest
import httpx

from async_api_fetcher.services import fetch_user
from async_api_fetcher.models import UserResponse


@pytest.mark.asyncio
async def test_no_cache_skips_cache_operations():

    # Mock the HTTP response (synchronous methods)
    mock_response = Mock()

    mock_response.status_code = 200

    mock_response.json.return_value = {
        "id": 1,
        "name": "Leanne Graham",
        "email": "test@example.com",
        "address": {
            "city": "Gwenborough"
        }
    }

    mock_response.raise_for_status.return_value = None

    # Mock the asynchronous HTTP client
    mock_client = AsyncMock(spec=httpx.AsyncClient)

    mock_client.get.return_value = mock_response

    with (
        patch(
            "async_api_fetcher.services.load_cache"
        ) as mock_load,

        patch(
            "async_api_fetcher.services.save_cache"
        ) as mock_save,
    ):

        result = await fetch_user(
            mock_client,
            1,
            use_cache=False
        )

        # Verify Pydantic validation
        assert result.id == 1
        assert result.name == "Leanne Graham"
        assert result.city == "Gwenborough"

        # Verify cache operations were skipped
        mock_load.assert_not_called()
        mock_save.assert_not_called()

        # Verify HTTP request was executed
        mock_client.get.assert_awaited_once()

@pytest.mark.asyncio
async def test_cache_enabled_reads_cache():

    cached_data = {
        "id": 1,
        "name": "Leanne Graham",
        "email": "test@example.com",
        "city": "Gwenborough"
    }

    mock_client = AsyncMock(spec=httpx.AsyncClient)

    with (
        patch(
            "async_api_fetcher.services.load_cache",
            return_value=cached_data
        ) as mock_load,

        patch(
            "async_api_fetcher.services.save_cache"
        ) as mock_save,
    ):

        result = await fetch_user(
            mock_client,
            1,
            use_cache=True
        )

        assert isinstance(result, UserResponse)

        assert result.id == 1
        assert result.name == "Leanne Graham"

        mock_load.assert_called_once_with("user:1")
        mock_client.get.assert_not_awaited()
        mock_save.assert_not_called()
