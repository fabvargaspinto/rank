from config.turso_settings import TursoSettings, is_sqlite_url
from core.instagram.infrastructure.sql import SqlDatabase
from core.instagram.infrastructure.sqlite_db import SqliteDatabase
from core.instagram.infrastructure.turso_db import TursoHttpDatabase


def create_instagram_db(settings: TursoSettings) -> SqlDatabase:
    url = settings.turso_database_url.strip()
    if is_sqlite_url(url):
        return SqliteDatabase(url)
    return TursoHttpDatabase(url, settings.turso_auth_token)
