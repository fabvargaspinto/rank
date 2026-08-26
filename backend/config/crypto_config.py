from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


class CryptoConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    email_fernet_key: str = Field(alias="EMAIL_FERNET_KEY")
    email_hmac_key: str = Field(alias="EMAIL_HMAC_KEY")
