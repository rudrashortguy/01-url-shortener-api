"""Application settings via pydantic-settings."""

from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "URL Shortener API"
    app_version: str = "1.0.0"
    redis_url: str = "redis://localhost:6379/0"
    base_url: str = "http://localhost:8000"
    short_code_length: int = 6

    model_config = {
        "env_prefix": "URLSHORTENER_",
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


settings = Settings()