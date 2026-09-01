import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App
    ENVIRONMENT: str = "development"
    SECRET_KEY: str = "dev_secret_key_selfmanual_v1_3"
    PORT: int = 8000
    WEBHOOK_DOMAIN: str = "http://localhost:8000"

    # Telegram
    TELEGRAM_BOT_TOKEN: str = ""

    # Supabase PostgreSQL
    SUPABASE_DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres"
    SUPABASE_URL: Optional[str] = None
    SUPABASE_SERVICE_KEY: Optional[str] = None

    # Prodamus
    PRODAMUS_SECRET_KEY: str = ""
    PRODAMUS_PAYMENT_URL: str = "https://payform.ru"

    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Admin Users
    ADMIN_USERNAMES: str = "astihakun,astikkhakun,sherlockdxb"

    @property
    def admin_usernames_list(self) -> list[str]:
        return [u.strip().lstrip("@").lower() for u in self.ADMIN_USERNAMES.split(",") if u.strip()]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
