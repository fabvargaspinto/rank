import os
from pathlib import Path

import pytest
from postgrest.exceptions import APIError
from supabase import ClientOptions, create_client

from config.crypto_settings import CryptoSettings
from config.db_settings import DBSettings
from config.turso_settings import TursoSettings
from core.auth.infrastructure.auth_supabase_repo import AuthSupabaseRepo
from core.auth.infrastructure.email_crypto import EmailCrypto
from core.instagram.infrastructure.db import create_instagram_db
from core.shared.infrastructure.supabase_client import DBClient
from tests.integration.local_supabase import (
    configure_integration_supabase_env,
    configure_turso_development_env,
    ensure_integration_supabase_ready,
)


def _instagram_only(session: pytest.Session) -> bool:
    items = getattr(session, "items", [])
    if not items:
        return False
    return all("/instagram/" in Path(str(item.fspath)).as_posix() for item in items)


def _in_ci() -> bool:
    return os.getenv("CI", "").strip().lower() in {"1", "true", "yes"}


@pytest.fixture(scope="session", autouse=True)
def require_integration_supabase(request: pytest.FixtureRequest) -> None:
    if _instagram_only(request.session):
        return
    try:
        url = configure_integration_supabase_env()
    except RuntimeError as exc:
        if _in_ci():
            pytest.fail(str(exc))
        pytest.skip(str(exc))
    if not ensure_integration_supabase_ready(url):
        message = (
            "Supabase de desarrollo no responde. "
            "Revisá SUPABASE_DEVELOPMENT_URL o levantá el stack local con "
            "`pnpm --dir frontend supabase:start`."
        )
        if _in_ci():
            pytest.fail(message)
        pytest.skip(message)


@pytest.fixture(scope="session")
def db_settings() -> DBSettings:
    return DBSettings()


@pytest.fixture(scope="session")
def db_client(db_settings: DBSettings) -> DBClient:
    return DBClient(db_settings)


@pytest.fixture(scope="session")
def users_table(db_client: DBClient) -> DBClient:
    try:
        db_client.get_db().table("users").select("id").limit(1).execute()
    except APIError as exc:
        if exc.code == "PGRST205":
            message = (
                "La tabla public.users no existe. Aplicá las migraciones de "
                "supabase/migrations (`supabase db reset` o `supabase db push`)."
            )
            if _in_ci():
                pytest.fail(message)
            pytest.skip(message)
        raise
    return db_client


@pytest.fixture(scope="session")
def anon_client(db_settings: DBSettings):
    return create_client(
        db_settings.supabase_url,
        os.environ["SUPABASE_ANON_KEY"],
        options=ClientOptions(
            auto_refresh_token=False,
            persist_session=False,
        ),
    )


@pytest.fixture(scope="session")
def email_crypto() -> EmailCrypto:
    return EmailCrypto(CryptoSettings())


@pytest.fixture(scope="session")
def auth_repo(users_table: DBClient, email_crypto: EmailCrypto) -> AuthSupabaseRepo:
    return AuthSupabaseRepo(users_table, email_crypto)


@pytest.fixture(scope="session")
def turso_development_db():
    if not configure_turso_development_env():
        pytest.skip(
            "Falta TURSO_DEVELOPMENT_URL (o TURSO_DEVELOPMENT_DATABASE) y "
            "TURSO_DEVELOPMENT_TOKEN para los tests de Instagram contra Turso."
        )
    db = create_instagram_db(TursoSettings())
    try:
        yield db
    finally:
        close = getattr(db, "close", None)
        if callable(close):
            close()
