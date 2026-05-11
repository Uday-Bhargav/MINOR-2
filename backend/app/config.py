from functools import lru_cache
from typing import Literal

from pydantic import AnyHttpUrl, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: str = "http://localhost:5173"

    supabase_url: AnyHttpUrl | None = None
    supabase_service_role_key: str | None = None

    news_provider: Literal["newsapi", "gnews"] = "gnews"
    news_api_key: str | None = None
    gnews_api_key: str | None = None

    ai_provider: Literal["openai", "anthropic", "groq", "demo"] = "demo"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-3-5-sonnet-latest"
    groq_api_key: str | None = None
    groq_model: str = "llama-3.3-70b-versatile"

    refresh_minutes: int = Field(default=15, ge=1)

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def has_supabase(self) -> bool:
        return bool(self.supabase_url and self.supabase_service_role_key)

    @field_validator("supabase_url", mode="before")
    @classmethod
    def empty_url_to_none(cls, value: str | None):
        return None if value == "" else value


@lru_cache
def get_settings() -> Settings:
    return Settings()
