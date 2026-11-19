import asyncio
import time
import httpx
import statistics

from async_api_fetcher.services import (
    fetch_user,
    fetch_weather,
    fetch_country
)
from async_api_fetcher.cache import delete_cache


def calculate_median(times: list[float]) -> float:
    return statistics.median(times)

def clear_benchmark_cache():

    delete_cache("user:1")
    delete_cache("weather:delhi")
    delete_cache("country:sweden")


async def sequential_execution(client):

    start = time.perf_counter()

    user = await fetch_user(client, 1)
    weather = await fetch_weather(client, "Delhi")
    country = await fetch_country(client, "Sweden")

    elapsed = time.perf_counter() - start

    return [user, weather, country], elapsed


async def concurrent_execution(client):

    start = time.perf_counter()

    results = await asyncio.gather(
        fetch_user(client, 1),
        fetch_weather(client, "Delhi"),
        fetch_country(client, "Sweden")
    )

    elapsed = time.perf_counter() - start

    return results, elapsed


async def main():

    sequential_times = []
    concurrent_times = []

    runs = 5

    async with httpx.AsyncClient(timeout=15.0) as client:

        # Sequential benchmarks
        print("\nSEQUENTIAL BENCHMARK")

        for run in range(runs):

            clear_benchmark_cache()

            _, elapsed = await sequential_execution(client)

            sequential_times.append(elapsed)

            print(f"Run {run + 1}: {elapsed:.2f} seconds")

        # Concurrent benchmarks
        print("\nCONCURRENT BENCHMARK")

        for run in range(runs):

            clear_benchmark_cache()

            _, elapsed = await concurrent_execution(client)

            concurrent_times.append(elapsed)

            print(f"Run {run + 1}: {elapsed:.2f} seconds")

    # Calculate median values
    sequential_median = calculate_median(sequential_times)
    concurrent_median = calculate_median(concurrent_times)

    # Calculate average values
    sequential_average = statistics.mean(sequential_times)
    concurrent_average = statistics.mean(concurrent_times)

    # Display results
    print("\nREAL API BENCHMARK RESULTS")
    print("=" * 40)

    print("\nSEQUENTIAL")
    print(f"Median: {sequential_median:.2f} seconds")
    print(f"Average: {sequential_average:.2f} seconds")

    print("\nCONCURRENT")
    print(f"Median: {concurrent_median:.2f} seconds")
    print(f"Average: {concurrent_average:.2f} seconds")

    if concurrent_median > 0:
        speedup = sequential_median / concurrent_median

        print("\nPERFORMANCE")
        print(f"Median speedup: {speedup:.2f}x")


if __name__ == "__main__":
    asyncio.run(main())