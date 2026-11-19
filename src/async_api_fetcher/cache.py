import hashlib
import json
import logging
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

CACHE_DIR = Path("cache")


def get_cache_path(key: str) -> Path:
    """Generate a unique cache filename."""

    safe_key = hashlib.sha256(key.encode("utf-8")).hexdigest()

    return CACHE_DIR / f"{safe_key}.json"


def save_cache(key: str, data: dict[str, Any], ttl: int) -> None:

    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    cache_data = {"cached_at": time.time(), "ttl": ttl, "data": data}

    cache_file = get_cache_path(key)

    with cache_file.open("w", encoding="utf-8") as f:
        json.dump(cache_data, f, indent=4)

    logger.debug("Cache saved: %s", key)


def load_cache(key: str) -> dict[str, Any] | None:

    cache_file = get_cache_path(key)

    if not cache_file.exists():
        return None

    try:
        with cache_file.open("r", encoding="utf-8") as f:
            cached_data = json.load(f)

        if not isinstance(cached_data, dict):
            raise TypeError("Invalid cache structure")

        cached_at = cached_data["cached_at"]
        ttl = cached_data["ttl"]
        data = cached_data["data"]

        if (
            not isinstance(cached_at, (int, float))
            or isinstance(cached_at, bool)
            or not isinstance(ttl, (int, float))
            or isinstance(ttl, bool)
            or ttl < 0
        ):
            raise ValueError("Invalid cache metadata")

        if time.time() - cached_at > ttl:
            logger.info("Cache expired: %s", key)
            delete_cache(key)
            return None

        if not isinstance(data, dict):
            raise TypeError("Invalid cached data")

        logger.debug("Cache hit: %s", key)

        return data

    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError):
        logger.warning("Corrupted cache detected: %s", key)

        delete_cache(key)

        return None


def delete_cache(key: str) -> None:

    cache_file = get_cache_path(key)
    try:
        cache_file.unlink(missing_ok=True)
        logger.debug("Cache deleted: %s", key)

    except OSError:
        logger.exception("Failed to delete cache: %s", key)
