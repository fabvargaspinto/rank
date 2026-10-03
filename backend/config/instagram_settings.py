from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings

from config.env import settings_config

_HEX_32_BYTES = r"^[0-9a-fA-F]{64}$"


class InstagramSettings(BaseSettings):
    instagram_app_id: str = Field(
        min_length=1,
        validation_alias=AliasChoices(
            "INSTAGRAM_APP_ID",
            "META_APP_ID",
            "META_ID_APP",
        ),
    )
    instagram_app_secret: str = Field(
        min_length=1,
        validation_alias=AliasChoices(
            "INSTAGRAM_APP_SECRET",
            "META_APP_SECRET",
        ),
    )
    instagram_redirect_uri: str = Field(
        validation_alias=AliasChoices(
            "INSTAGRAM_REDIRECT_URI",
            "META_INSTAGRAM_REDIRECT_URI",
            "META_CALLBACK_URL",
        ),
    )
    instagram_token_encryption_key: str = Field(pattern=_HEX_32_BYTES)
    instagram_snapshot_job_token: str = ""

    model_config = settings_config(populate_by_name=True)

    @property
    def token_encryption_key_bytes(self) -> bytes:
        return bytes.fromhex(self.instagram_token_encryption_key)
