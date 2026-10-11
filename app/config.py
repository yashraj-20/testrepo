"""Runtime configuration."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings loaded from the environment.

    Environment variables use the ``TASK_`` prefix, for example
    ``TASK_DATABASE_URL``.
    """

    app_name: str = "Task API"
    database_url: str = "sqlite:///./tasks.db"

    model_config = SettingsConfigDict(env_prefix="TASK_", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
