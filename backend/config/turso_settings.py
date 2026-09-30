from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class TursoSettings(BaseSettings):
    turso_database_url: str = Field(
        default="file:./instagram.db",
        validation_alias=AliasChoices("TURSO_URL", "TURSO_DATABASE_URL"),
    )
    turso_auth_token: str = Field(
        default="",
        validation_alias=AliasChoices("TURSO_TOKEN", "TURSO_AUTH_TOKEN"),
    )

    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )
