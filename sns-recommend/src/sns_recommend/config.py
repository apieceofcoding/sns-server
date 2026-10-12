from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    source_database_url: str = "postgresql://snsuser:snspassword@localhost:5432/snsdb"
    redis_url: str = "redis://localhost:56379/0"
    cursor_secret: str = "course-local-cursor-secret"
    snapshot_ttl: int = 1800


@lru_cache
def settings() -> Settings:
    return Settings()
