
import pytest
from pydantic import ValidationError

from async_api_fetcher.config import Settings


def test_default_settings():

    config = Settings(_env_file=None)

    assert config.http_timeout == 15.0
    assert config.max_retries == 3
    assert config.user_ttl == 3600
    assert config.weather_ttl == 300
    assert config.country_ttl == 86400


def test_custom_settings():

    config = Settings(
        _env_file=None,
        http_timeout=20,
        max_retries=5,
        weather_ttl=600
    )

    assert config.http_timeout == 20
    assert config.max_retries == 5
    assert config.weather_ttl == 600


def test_invalid_timeout():

    with pytest.raises(ValidationError):

        Settings(
            _env_file=None,
            http_timeout=-5
        )


def test_invalid_retries():

    with pytest.raises(ValidationError):

        Settings(
            _env_file=None,
            max_retries=0
        )
