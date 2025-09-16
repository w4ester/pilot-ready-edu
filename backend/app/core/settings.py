"""Application settings using pydantic BaseSettings."""

from functools import lru_cache

from pydantic import BaseSettings


class Settings(BaseSettings):
    environment: str = "development"
    database_url: str = "postgresql+psycopg://app:app@db:5432/appdb"
    redis_url: str = "redis://redis:6379/0"
    ollama_host: str = "http://ollama:11434"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Return cached settings instance."""

    return Settings()
