# backend/app/core/config.py
from pydantic import BaseSettings, AnyHttpUrl
from functools import lru_cache
from typing import List

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "EY Agentic Drug Platform"

    # External services, DBs
    MONGO_URI: str = "mongodb://localhost:27017"
    REDIS_URL: str = "redis://localhost:6379"
    SUPABASE_URL: AnyHttpUrl | None = None
    SUPABASE_KEY: str | None = None

    # Queue
    REPORT_QUEUE_NAME: str = "report-generation"

    class Config:
        env_file = ".env"

@lru_cache
def get_settings() -> Settings:
    return Settings()
