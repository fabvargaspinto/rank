from pydantic_settings import BaseSettings

from config.env import settings_config


class CryptoSettings(BaseSettings):
    email_encryption_key: str
    email_hmac_key: str

    model_config = settings_config()

    @property
    def email_encryption_key_bytes(self) -> bytes:
        return bytes.fromhex(self.email_encryption_key)

    @property
    def email_hmac_key_bytes(self) -> bytes:
        return bytes.fromhex(self.email_hmac_key)
