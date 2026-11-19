import asyncio
import logging
import time

import httpx

from async_api_fetcher.cli import parse_arguments
from async_api_fetcher.config import settings
from async_api_fetcher.services import fetch_country, fetch_user, fetch_weather

logger = logging.getLogger("async_api_fetcher")


# Application orchestration
async def async_main(args) -> None:

    print("\n=================================")
    print("     ASYNC MULTI-API FETCHER")
    print("=================================")

    print(f"\nUser ID          : {args.user_id}")
    print(f"Weather Location : {args.weather_location}")
    print(f"Country          : {args.country}")

    logger.info("Fetching data from APIs...")

    async with httpx.AsyncClient(timeout=settings.http_timeout) as client:
        use_cache = not args.no_cache

        logger.info(f"Cache enabled: {use_cache}")

        results = await asyncio.gather(
            fetch_user(client, args.user_id, use_cache=use_cache),
            fetch_weather(client, args.weather_location, use_cache=use_cache),
            fetch_country(client, args.country, use_cache=use_cache),
            return_exceptions=True,
        )

    api_names = ["USER API", "WEATHER API", "COUNTRY API"]

    units = {
        "temperature": "°C",
        "humidity": "%",
        "wind_speed": "km/h",
        "population": "people",
    }

    for name, result in zip(api_names, results):
        print(f"\n{name}")
        print("-" * 35)

        if isinstance(result, Exception):
            logger.error(f"API failed: {result}")
            continue

        for key, value in result.model_dump().items():
            label = key.replace("_", " ").title()
            unit = units.get(key, "")

            if key == "population" and value is not None:
                value = f"{value:,}"

            print(f"{label}: {value} {unit}".rstrip())

    print("\n=================================")
    print("All API requests completed.")
    print("=================================")


# Synchronous CLI entry point
def main() -> None:

    args = parse_arguments()
    start = time.perf_counter()
    asyncio.run(async_main(args))
    end = time.perf_counter()
    print(f"\nExecution time: {end - start:.2f} seconds")


if __name__ == "__main__":
    main()
