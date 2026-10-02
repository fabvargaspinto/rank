from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings

from config.env import settings_config


def is_sqlite_url(url: str) -> bool:
    normalized = url.strip().lower()
    return (
        normalized in {":memory:", "sqlite:///:memory:"}
        or normalized.startswith("file:")
        or normalized.endswith(".db")
        or normalized.startswith("sqlite:")
    )


class TursoSettings(BaseSettings):
    turso_database_url: str = Field(
        default="file:./instagram.db",
        validation_alias=AliasChoices("TURSO_URL", "TURSO_DATABASE_URL"),
    )
    turso_auth_token: str = Field(
        default="",
        validation_alias=AliasChoices("TURSO_TOKEN", "TURSO_AUTH_TOKEN"),
    )

    model_config = settings_config(populate_by_name=True)

    def require_remote_for_production(self) -> None:
        url = self.turso_database_url.strip()
        token = self.turso_auth_token.strip()
        if is_sqlite_url(url):
            raise RuntimeError(
                "En producción TURSO_URL no puede ser SQLite "
                "(file:… / *.db). Usá una URL de Turso Cloud."
            )
        if not token:
            raise RuntimeError(
                "En producción falta TURSO_TOKEN (o TURSO_AUTH_TOKEN)."
            )
