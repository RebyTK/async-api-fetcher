
import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from async_api_fetcher.main import async_main
from async_api_fetcher.models import (
    UserResponse,
    WeatherResponse,
    CountryResponse
)


def make_args():
    return SimpleNamespace(
        user_id=1,
        weather_location="Delhi",
        country="Sweden",
        no_cache=False
    )


@pytest.mark.asyncio
async def test_one_api_failure_does_not_stop_others(
    capsys,
    caplog
):

    mock_user = AsyncMock(
        side_effect=RuntimeError("User API unavailable")
    )

    mock_weather = AsyncMock(
        return_value=WeatherResponse(
            location="Delhi",
            country="India",
            temperature=25.0,
            humidity=45.0,
            wind_speed=7.2
        )
    )

    mock_country = AsyncMock(
        return_value=CountryResponse(
            name="Sweden",
            population=10621725,
            region="Europe"
        )
    )

    with (
        patch(
            "async_api_fetcher.main.fetch_user",
            new=mock_user
        ),
        patch(
            "async_api_fetcher.main.fetch_weather",
            new=mock_weather
        ),
        patch(
            "async_api_fetcher.main.fetch_country",
            new=mock_country
        ),
    ):

        await async_main(make_args())

    # All APIs must execute
    mock_user.assert_awaited_once()
    mock_weather.assert_awaited_once()
    mock_country.assert_awaited_once()

    # Check error logging
    assert "API failed: User API unavailable" in caplog.text

    # Check successful API output
    output = capsys.readouterr().out

    assert "Delhi" in output
    assert "Sweden" in output


@pytest.mark.asyncio
async def test_all_apis_execute_concurrently():

    started_count = 0

    all_started = asyncio.Event()
    release = asyncio.Event()

    async def mock_api(result):

        nonlocal started_count

        started_count += 1

        if started_count == 3:
            all_started.set()

        await release.wait()

        return result

    user_result = UserResponse(
        id=1,
        name="Leanne Graham",
        email="test@example.com",
        city="Gwenborough"
    )

    weather_result = WeatherResponse(
        location="Delhi",
        country="India",
        temperature=25.0,
        humidity=45.0,
        wind_speed=7.2
    )

    country_result = CountryResponse(
        name="Sweden",
        population=10621725,
        region="Europe"
    )

    # Explicitly asynchronous mock functions
    async def mock_user(*args, **kwargs):
        return await mock_api(user_result)

    async def mock_weather(*args, **kwargs):
        return await mock_api(weather_result)

    async def mock_country(*args, **kwargs):
        return await mock_api(country_result)

    with (
        patch(
            "async_api_fetcher.main.fetch_user",
            new=mock_user
        ),
        patch(
            "async_api_fetcher.main.fetch_weather",
            new=mock_weather
        ),
        patch(
            "async_api_fetcher.main.fetch_country",
            new=mock_country
        ),
    ):

        task = asyncio.create_task(
            async_main(make_args())
        )

        try:

            await asyncio.wait_for(
                all_started.wait(),
                timeout=2.0
            )

            assert started_count == 3

        finally:

            release.set()

        await task
