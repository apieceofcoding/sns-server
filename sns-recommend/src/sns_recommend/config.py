from functools import lru_cache
from typing import Literal
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str = "postgresql://recommend:recommend@localhost:55432/recommend"
    redis_url: str = "redis://localhost:56379/0"
    internal_token: str = "course-local-token"
    model_mode: Literal["fixture", "live", "record", "replay"] = "fixture"
    google_api_key: SecretStr = SecretStr("")
    embedding_model: str = "gemini-embedding-2"
    rerank_model: str = "gemini-3.5-flash-lite"
    dimensions: int = 768
    snapshot_ttl: int = 1800
    refresh_seconds: int = 300
    lease_seconds: int = 120
    daily_call_limit: int = 20
    recordings_dir: str = "recordings"


@lru_cache
def settings() -> Settings:
    return Settings()
