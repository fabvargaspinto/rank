import pytest

from config.turso_settings import TursoSettings


def test_require_remote_rejects_sqlite_in_production():
    settings = TursoSettings(
        turso_database_url="file:./instagram.db",
        turso_auth_token="tok",
    )

    with pytest.raises(RuntimeError, match="no puede ser SQLite"):
        settings.require_remote_for_production()


def test_require_remote_rejects_missing_token():
    settings = TursoSettings(
        turso_database_url="libsql://socials.turso.io",
        turso_auth_token="   ",
    )

    with pytest.raises(RuntimeError, match="falta TURSO_TOKEN"):
        settings.require_remote_for_production()


def test_require_remote_accepts_turso_cloud():
    settings = TursoSettings(
        turso_database_url="libsql://socials.turso.io",
        turso_auth_token="secret-token",
    )

    settings.require_remote_for_production()
