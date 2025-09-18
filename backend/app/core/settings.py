"""Application settings using Pydantic v2 BaseSettings."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    environment: str = "development"
    database_url: str = "postgresql+psycopg://app:app@db:5432/appdb"
    redis_url: str = "redis://redis:6379/0"
    ollama_host: str = "http://ollama:11434"
    dev_user_id: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    """Return cached settings instance."""

    return Settings()
