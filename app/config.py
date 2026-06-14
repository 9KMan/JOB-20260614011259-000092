from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    app_name: str = "RingCentral Call Summary Pipeline"
    app_version: str = "1.0.0"
    debug: bool = False
    secret_key: str = "change-me-in-production"

    database_url: str = Field(
        default="postgresql://postgres:***@localhost:5432/ringcentral_db",
        alias="DATABASE_URL",
    )

    redis_url: str = Field(
        default="redis://localhost:6379/0",
        alias="REDIS_URL",
    )

    jwt_secret_key: str = Field(
        default="change-me-jwt-secret",
        alias="JWT_SECRET_KEY",
    )

    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    ringcentral_client_id: str = Field(
        default="",
        alias="RINGCENTRAL_CLIENT_ID",
    )

    ringcentral_client_secret: str = Field(
        default="",
        alias="RINGCENTRAL_CLIENT_SECRET",
    )

    openai_api_key: str = Field(
        default="",
        alias="OPENAI_API_KEY",
    )

    anthropic_api_key: str = Field(
        default="",
        alias="ANTHROPIC_API_KEY",
    )

    google_sheets_client_id: str = Field(
        default="",
        alias="GOOGLE_SHEETS_CLIENT_ID",
    )

    google_sheets_client_secret: str = Field(
        default="",
        alias="GOOGLE_SHEETS_CLIENT_SECRET",
    )

    cors_origins: list = ["http://localhost:3000"]

    celery_broker_url: str = Field(
        default="redis://localhost:6379/0",
        alias="CELERY_BROKER_URL",
    )

    celery_result_backend: str = Field(
        default="redis://localhost:6379/0",
        alias="CELERY_RESULT_BACKEND",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
