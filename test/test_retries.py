from unittest.mock import AsyncMock

import httpx
import pytest

from async_api_fetcher.services import get_json


@pytest.mark.asyncio
async def test_successful_request():

    client = AsyncMock(spec=httpx.AsyncClient)

    response = httpx.Response(
        200,
        json={"message": "success"},
        request=httpx.Request("GET", "https://example.com"),
    )

    client.get.return_value = response

    result = await get_json(client, "https://example.com")

    assert result == {"message": "success"}
    assert client.get.call_count == 1


@pytest.mark.asyncio
async def test_retry_on_503():

    client = AsyncMock(spec=httpx.AsyncClient)

    request = httpx.Request("GET", "https://example.com")

    responses = [
        httpx.Response(503, request=request),
        httpx.Response(503, request=request),
        httpx.Response(200, json={"message": "success"}, request=request),
    ]

    client.get.side_effect = responses

    result = await get_json(client, "https://example.com")

    assert result == {"message": "success"}
    assert client.get.call_count == 3


@pytest.mark.asyncio
async def test_no_retry_on_404():

    client = AsyncMock(spec=httpx.AsyncClient)

    request = httpx.Request("GET", "https://example.com")

    client.get.return_value = httpx.Response(404, request=request)

    with pytest.raises(RuntimeError, match="404"):
        await get_json(client, "https://example.com")

    assert client.get.call_count == 1


@pytest.mark.asyncio
async def test_retry_exhausted():

    client = AsyncMock(spec=httpx.AsyncClient)

    request = httpx.Request("GET", "https://example.com")

    client.get.return_value = httpx.Response(503, request=request)

    with pytest.raises(RuntimeError, match="after 3 attempts"):
        await get_json(client, "https://example.com", max_retries=3)

    assert client.get.await_count == 3
