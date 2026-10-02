from pydantic_settings import BaseSettings

from config.env import settings_config


class DBSettings(BaseSettings):
    supabase_url: str
    supabase_secret_key: str

    model_config = settings_config()
