# Async Multi-API Fetcher

An asynchronous Python CLI application that fetches user, weather, and country information from multiple public APIs concurrently.

Built with **Python, HTTPX, asyncio, Pydantic, and uv**, this project demonstrates practical API integration, asynchronous execution, caching, retry mechanisms, configuration management, and automated testing.

## Features

- **Asynchronous HTTP requests:** Uses HTTPX `AsyncClient` for non-blocking API communication.
- **Concurrent execution:** Fetches data from multiple APIs using `asyncio.gather()`.
- **Retry mechanism:** Implements exponential backoff for retryable HTTP and network errors.
- **Response validation:** Uses Pydantic models to validate API responses.
- **Caching:** Implements file-based JSON caching with configurable TTL.
- **Cache control:** Allows users to disable caching through a CLI argument.
- **Environment-based configuration:** Separates application settings from source code.
- **Logging:** Records API activity, cache operations, and failures.
- **Automated testing:** Uses pytest and pytest-asyncio to test application functionality.
- **Performance benchmarking:** Compares sequential and concurrent API execution.

## APIs Used

| API | Purpose | Information Retrieved |
|---|---|---|
| JSONPlaceholder | User information | ID, name, email, city |
| Open-Meteo | Weather information | Location, temperature, humidity, wind speed |
| REST Countries | Country information | Name, population, region |

## Tech Stack

- Python 3.12+
- HTTPX
- asyncio
- Pydantic
- pytest
- pytest-asyncio
- Ruff
- uv

## Project Structure

```text
async-api-fetcher/
│
├── src/
│   └── async_api_fetcher/
│       ├── __init__.py
│       ├── __main__.py
│       ├── main.py
│       ├── cli.py
│       ├── services.py
│       ├── models.py
│       ├── cache.py
│       ├── config.py
│       └── benchmark.py
│
├── test/
│   ├── test_cache.py
│   ├── test_cache_control.py
│   ├── test_concurrency.py
│   ├── test_config.py
│   ├── test_retries.py
│   └── test_services.py
│
├── cache/
├── pyproject.toml
├── uv.lock
├── .gitignore
└── README.md
```

*Adjust the tree if your actual filenames or directories differ.*

## Installation

### Prerequisites

- Python 3.12 or later
- Git
- uv package manager

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/async-api-fetcher.git

cd async-api-fetcher
```

### 2. Install dependencies

```bash
uv sync --all-groups
```

This installs the project dependencies