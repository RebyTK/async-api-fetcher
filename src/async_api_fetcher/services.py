import asyncio
import logging
import os
from typing import Any
from urllib.parse import quote

import httpx
from pydantic import ValidationError

from async_api_fetcher.cache import delete_cache, load_cache, save_cache
from async_api_fetcher.config import settings
from async_api_fetcher.models import CountryResponse, UserResponse, WeatherResponse

# Create a module-specific logger
logger = logging.getLogger(__name__)


async def get_json(
    client: httpx.AsyncClient,
    url: str,
    params: dict | None = None,
    headers: dict[str, str] | None = None,
    max_retries: int | None = None,
) -> Any:

    if max_retries is None:
        max_retries = settings.max_retries

    for attempt in range(max_retries):
        try:
            response = await client.get(url, params=params, headers=headers)

            response.raise_for_status()

            logger.debug("Successfully fetched data from %s", url)

            return response.json()

        except httpx.HTTPStatusError as exc:
            status_code = exc.response.status_code

            retryable_statuses = {429, 500, 502, 503, 504}

            if status_code not in retryable_statuses:
                logger.error("Non-retryable HTTP error %s from %s", status_code, url)

                raise RuntimeError(f"HTTP error: {status_code}") from exc

            if attempt == max_retries - 1:
                logger.error(
                    "HTTP error %s after %s attempts: %s", status_code, max_retries, url
                )

                raise RuntimeError(
                    f"HTTP error after {max_retries} attempts: {status_code}"
                ) from exc

            delay = 2**attempt

            logger.warning(
                "HTTP %s from %s. Retrying in %s seconds (attempt %s/%s)",
                status_code,
                url,
                delay,
                attempt + 1,
                max_retries,
            )

            await asyncio.sleep(delay)

        except httpx.RequestError as exc:
            if attempt == max_retries - 1:
                logger.error("Network error after %s attempts: %s", max_retries, exc)

                raise RuntimeError(
                    f"Network error after {max_retries} attempts: {exc}"
                ) from exc

            delay = 2**attempt

            logger.warning(
                "Network error: %s. Retrying in %s seconds (attempt %s/%s)",
                exc,
                delay,
                attempt + 1,
                max_retries,
            )

            await asyncio.sleep(delay)

        except ValueError as exc:
            logger.error("Invalid JSON response from %s: %s", url, exc)

            raise RuntimeError(f"Invalid JSON response: {exc}") from exc

    raise RuntimeError("Maximum retry attempts exceeded")


# API 1: User Information


async def fetch_user(
    client: httpx.AsyncClient, user_id: int, use_cache: bool = True
) -> UserResponse:

    cache_key = f"user:{user_id}"

    # Step 1: Read cache only when enabled
    if use_cache:
        cached_data = load_cache(cache_key)

        if cached_data is not None:
            try:
                logger.info("User API: Cache hit")

                return UserResponse.model_validate(cached_data)

            except ValidationError:
                logger.warning(
                    "Invalid user cache for ID %s. Fetching fresh data.", user_id
                )
                delete_cache(cache_key)

        logger.info("User API: Cache miss")

    else:
        logger.info("User API: Cache disabled")

    # Step 2: Fetch fresh data
    url = f"https://jsonplaceholder.typicode.com/users/{user_id}"

    data = await get_json(client, url)

    if not isinstance(data, dict):
        raise TypeError("Unexpected user response format")

    address = data.get("address") or {}

    # Step 3: Validate API response
    result = UserResponse.model_validate(
        {
            "id": data.get("id"),
            "name": data.get("name"),
            "email": data.get("email"),
            "city": address.get("city"),
        }
    )

    # Step 4: Save cache only when enabled
    if use_cache:
        save_cache(
            key=cache_key, data=result.model_dump(mode="json"), ttl=settings.user_ttl
        )

    logger.info("User API: Successfully fetched user %s", user_id)

    return result


# API 2: Weather Information
async def fetch_weather(
    client: httpx.AsyncClient, location: str, use_cache: bool = True
) -> WeatherResponse:

    cache_key = f"weather:{location.casefold()}"

    if use_cache:
        cached_data = load_cache(cache_key)

        if cached_data is not None:
            try:
                logger.info("Weather API: Cache hit")

                return WeatherResponse.model_validate(cached_data)

            except ValidationError:
                logger.warning(
                    "Invalid weather cache for %s. Fetching fresh data.", location
                )
                delete_cache(cache_key)

    logger.info("Weather API: Cache miss for %s", location)

    # Step 1: Convert city name into coordinates
    geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"

    geocoding_params = {
        "name": location,
        "count": 1,
        "language": "en",
        "format": "json",
    }

    geo_data = await get_json(client, geocoding_url, geocoding_params)

    if not isinstance(geo_data, dict):
        raise TypeError("Invalid geocoding response")

    locations = geo_data.get("results")

    if not isinstance(locations, list) or not locations:
        raise TypeError(f"Location not found: {location}")

    place = locations[0]

    if not isinstance(place, dict):
        raise TypeError("Invalid geocoding result")

    latitude = place["latitude"]
    longitude = place["longitude"]

    # Step 2: Fetch weather using coordinates
    weather_url = "https://api.open-meteo.com/v1/forecast"

    weather_params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": ("temperature_2m,relative_humidity_2m,wind_speed_10m"),
        "timezone": "auto",
    }

    data = await get_json(client, weather_url, weather_params)

    current = data.get("current")

    if not isinstance(current, dict):
        raise TypeError("Invalid weather response")

    result = WeatherResponse.model_validate(
        {
            "location": place.get("name"),
            "country": place.get("country"),
            "temperature": current.get("temperature_2m"),
            "humidity": current.get("relative_humidity_2m"),
            "wind_speed": current.get("wind_speed_10m"),
        }
    )

    logger.info("Weather API: Successfully fetched weather for %s", location)

    if use_cache:
        save_cache(
            key=cache_key, data=result.model_dump(mode="json"), ttl=settings.weather_ttl
        )
    return result


# API 3: Country Information
async def fetch_country(
    client: httpx.AsyncClient, country_name: str, use_cache: bool = True
) -> CountryResponse:

    cache_key = f"country:{country_name.casefold()}"

    if use_cache:
        cached_data = load_cache(cache_key)

        if cached_data is not None:
            try:
                logger.info("Country API: Cache hit")

                return CountryResponse.model_validate(cached_data)

            except ValidationError:
                logger.warning(
                    "Invalid country cache for %s. Fetching fresh data.", country_name
                )
                delete_cache(cache_key)

    logger.info("Country API: Cache miss for %s", country_name)

    url = (
        "https://api.restcountries.com/"
        f"countries/v5/names.common/{quote(country_name, safe='')}"
    )

    api_key = os.getenv("REST_COUNTRIES_API_KEY", "rc_live_demo")

    headers = {"Authorization": f"Bearer {api_key}"}

    params = {"response_fields": "names.common,population,region"}

    data = await get_json(client, url, params=params, headers=headers)

    if not isinstance(data, dict):
        raise TypeError("Invalid country response")

    response_data = data.get("data")

    if not isinstance(response_data, dict):
        raise TypeError("Missing country data")

    country_objects = response_data.get("objects")

    if not isinstance(country_objects, list) or not country_objects:
        raise TypeError("Country not found")

    country = country_objects[0]

    if not isinstance(country, dict):
        raise TypeError("Invalid country object")

    names = country.get("names")

    if not isinstance(names, dict):
        raise TypeError("Missing country names")

    result = CountryResponse.model_validate(
        {
            "name": names.get("common"),
            "population": country.get("population"),
            "region": country.get("region"),
        }
    )

    if use_cache:
        save_cache(
            key=cache_key, data=result.model_dump(mode="json"), ttl=settings.country_ttl
        )
    logger.info("Country API: Successfully fetched %s", country_name)
    return result
