from pathlib import Path

import pydantic_settings
from pydantic import Field


ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


class AppConfig(pydantic_settings.BaseSettings):
    model_config = pydantic_settings.SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    allowed_origins: list[str] = Field(alias="ALLOWED_ORIGINS")
