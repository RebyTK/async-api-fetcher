from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False
    )

    # HTTP configuration
    http_timeout: float = Field(
        default=15.0,
        gt=0
    )

    max_retries: int = Field(
        default=3,
        ge=1
    )

    # Cache configuration
    user_ttl: int = Field(
        default=3600,
        ge=0
    )

    weather_ttl: int = Field(
        default=300,
        ge=0
    )

    country_ttl: int = Field(
        default=86400,
        ge=0
    )


settings = Settings()
