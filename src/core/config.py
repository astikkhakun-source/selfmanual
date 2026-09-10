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
    ADMIN_USERNAMES: str = ""
    ADMIN_IDS: str = "189246266,260669598"
    TEST_GROUP_PROMO: str = "TESTGROUP2026"

    @property
    def admin_usernames_list(self) -> list[str]:
        return [u.strip().lstrip("@").lower() for u in self.ADMIN_USERNAMES.split(",") if u.strip()]

    @property
    def admin_ids_list(self) -> list[int]:
        res = []
        for i in self.ADMIN_IDS.split(","):
            i_str = i.strip()
            if i_str.isdigit():
                res.append(int(i_str))
        return res

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
