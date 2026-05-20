# app/core/config.py
import json
from functools import lru_cache
from typing import Literal

from pydantic import AnyUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralized application settings loaded from environment variables."""

    # ======================================================
    # APPLICATION
    # ======================================================
    APP_NAME: str = "TalaTrivia API"
    APP_VERSION: str = "1.0.0"

    APP_ENV: Literal[
        "development",
        "production",
        "test",
    ] = "development"

    API_V1_PREFIX: str = "/api/v1"

    # ======================================================
    # SECURITY
    # ======================================================
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ======================================================
    # DATABASE
    # ======================================================
    DATABASE_URL: AnyUrl

    # ======================================================
    # CORS
    # ======================================================
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
    ]

    # ======================================================
    # LOGGING
    # ======================================================
    LOG_LEVEL: str = "INFO"

    SQL_ECHO: bool = False

    # ======================================================
    # PYDANTIC SETTINGS
    # ======================================================
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            try:
                parsed = json.loads(value)

                if not isinstance(parsed, list):
                    raise ValueError("BACKEND_CORS_ORIGINS must be a JSON array")

                return [str(origin) for origin in parsed]
            except json.JSONDecodeError as exc:
                raise ValueError("Invalid BACKEND_CORS_ORIGINS JSON format") from exc

        return value

    @field_validator("JWT_SECRET_KEY")
    @classmethod
    def validate_jwt_secret_key(cls, value: str) -> str:
        """Validate JWT secret key security requirements."""
        if len(value) < 32:
            raise ValueError("JWT_SECRET_KEY must contain at least 32 characters")

        return value


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings instance."""
    return Settings()  # type: ignore[call-arg]


settings = get_settings()
