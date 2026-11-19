from unittest.mock import AsyncMock, Mock, patch

import pytest
import httpx

from async_api_fetcher.services import fetch_user
from async_api_fetcher.models import UserResponse


@pytest.mark.asyncio
async def test_fetch_user_success():

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

    mock_client = AsyncMock(spec=httpx.AsyncClient)

    mock_client.get.return_value = mock_response

    with (
        patch(
            "async_api_fetcher.services.load_cache",
            return_value=None
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

        # Verify Pydantic model
        assert isinstance(result, UserResponse)

        # Verify returned information
        assert result.id == 1
        assert result.name == "Leanne Graham"
        assert result.city == "Gwenborough"

        # Verify cache was checked
        mock_load.assert_called_once_with("user:1")

        # Verify API was called
        mock_client.get.assert_awaited_once()

        # Verify fresh data was cached
        mock_save.assert_called_once()


@pytest.mark.asyncio
async def test_fetch_user_invalid_response():

    mock_response = Mock()

    mock_response.json.return_value = [
        {"unexpected": "data"}
    ]

    mock_response.raise_for_status.return_value = None

    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.get.return_value = mock_response

    with patch(
        "async_api_fetcher.services.load_cache",
        return_value=None
    ):

        with pytest.raises(
            ValueError,
            match="Unexpected user response format"
        ):
            await fetch_user(
                mock_client,
                1,
                use_cache=True
            )


@pytest.mark.asyncio
async def test_fetch_user_retries_after_503():

    mock_response_503 = Mock()
    mock_response_503.status_code = 503

    mock_response_503.raise_for_status.side_effect = (
        httpx.HTTPStatusError(
            "Service unavailable",
            request=Mock(),
            response=Mock(
                status_code=503,
                request=Mock()
            )
        )
    )

    mock_response_200 = Mock()
    mock_response_200.status_code = 200

    mock_response_200.raise_for_status.return_value = None

    mock_response_200.json.return_value = {
        "id": 1,
        "name": "Leanne Graham",
        "email": "test@example.com",
        "address": {
            "city": "Gwenborough"
        }
    }

    mock_client = AsyncMock(spec=httpx.AsyncClient)

    mock_client.get.side_effect = [
        mock_response_503,
        mock_response_200
    ]

    with (
        patch(
            "async_api_fetcher.services.load_cache",
            return_value=None
        ),
        patch(
            "async_api_fetcher.services.save_cache"
        ),
        patch(
            "async_api_fetcher.services.asyncio.sleep",
            new_callable=AsyncMock
        ) as mock_sleep,
    ):

        result = await fetch_user(
            mock_client,
            1,
            use_cache=True
        )

        assert isinstance(result, UserResponse)
        assert result.name == "Leanne Graham"

        assert mock_client.get.await_count == 2
        mock_sleep.assert_awaited_once_with(1)
