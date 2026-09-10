# config/db_settings.py

from pydantic_settings import BaseSettings, SettingsConfigDict


class DBSettings(BaseSettings):
    supabase_url: str
    supabase_secret_key: str

    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
        extra="ignore",
    )