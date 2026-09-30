from config.turso_settings import TursoSettings
from core.instagram.infrastructure.sql import SqlDatabase
from core.instagram.infrastructure.sqlite_db import SqliteDatabase
from core.instagram.infrastructure.turso_db import TursoHttpDatabase


def is_sqlite_url(url: str) -> bool:
    normalized = url.strip().lower()
    return (
        normalized in {":memory:", "sqlite:///:memory:"}
        or normalized.startswith("file:")
        or normalized.endswith(".db")
        or normalized.startswith("sqlite:")
    )


def create_instagram_db(settings: TursoSettings) -> SqlDatabase:
    url = settings.turso_database_url.strip()
    if is_sqlite_url(url):
        return SqliteDatabase(url)
    return TursoHttpDatabase(url, settings.turso_auth_token)
