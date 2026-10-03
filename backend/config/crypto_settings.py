from pydantic import Field
from pydantic_settings import BaseSettings

from config.env import settings_config

_HEX_32_BYTES = r"^[0-9a-fA-F]{64}$"


class CryptoSettings(BaseSettings):
    email_encryption_key: str = Field(pattern=_HEX_32_BYTES)
    email_hmac_key: str = Field(pattern=_HEX_32_BYTES)

    model_config = settings_config()

    @property
    def email_encryption_key_bytes(self) -> bytes:
        return bytes.fromhex(self.email_encryption_key)

    @property
    def email_hmac_key_bytes(self) -> bytes:
        return bytes.fromhex(self.email_hmac_key)
