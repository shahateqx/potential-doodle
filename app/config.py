"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """All app settings, loaded from .env file or environment variables."""

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://widget_user:widget_pass@localhost:5433/widget_platform"
    DATABASE_URL_SYNC: str = "postgresql://widget_user:widget_pass@localhost:5433/widget_platform"

    # Auth
    SECRET_KEY: str = "change-me-to-a-random-64-char-string"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Geo Enrichment Providers
    GEO_PROVIDER_A_URL: str = "http://ip-api.com/json/"
    GEO_PROVIDER_B_URL: str = "https://ipapi.co/"
    GEO_PROVIDER_A_ENABLED: bool = True
    GEO_PROVIDER_B_ENABLED: bool = True

    # Email / Side Effect
    EMAIL_ENABLED: bool = True
    SMTP_HOST: str = "localhost"
    SMTP_PORT: int = 1025
    SMTP_FROM: str = "noreply@widget-platform.local"

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 30
    RATE_LIMIT_BURST: int = 10

    # App
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    WIDGET_BASE_URL: str = "http://localhost:8000"
    CORS_ALLOWED_ORIGINS: str = "*"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
