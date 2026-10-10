from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    # SNS app database. Accounts and posts stay there and are never copied.
    source_database_url: str = "postgresql://snsuser:snspassword@localhost:5432/snsdb"
    redis_url: str = "redis://localhost:56379/0"
    internal_token: str = "course-local-token"
    model_mode: str = "fixture"
    embedding_model: str = "gemini-embedding-2"
    rerank_model: str = "gemini-3.5-flash-lite"
    dimensions: int = 32
    snapshot_ttl: int = 1800
    refresh_seconds: int = 300
    lease_seconds: int = 120
    daily_call_limit: int = 20
    recordings_dir: str = "recordings"


@lru_cache
def settings() -> Settings:
    return Settings()
