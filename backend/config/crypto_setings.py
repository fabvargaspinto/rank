# config/crypto_settings.py

from pydantic_settings import BaseSettings, SettingsConfigDict


class CryptoSettings(BaseSettings):
    email_encryption_key: str
    email_hmac_key: str

    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def email_encryption_key_bytes(self) -> bytes:
        return bytes.fromhex(self.email_encryption_key)

    @property
    def email_hmac_key_bytes(self) -> bytes:
        return bytes.fromhex(self.email_hmac_key)
