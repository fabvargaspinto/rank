import os

import pytest
from postgrest.exceptions import APIError
from supabase import ClientOptions, create_client

from config.crypto_setings import CryptoSettings
from config.db_settings import DBSettings
from core.auth.infrastructure.auth_supabase_repo import AuthSupabaseRepo
from core.auth.infrastructure.email_crypto import EmailCrypto
from db.db_client import DBClient
from tests.integration.local_supabase import (
    configure_local_supabase_env,
    ensure_local_supabase_running,
)


@pytest.fixture(scope="session", autouse=True)
def require_local_supabase() -> None:
    url = configure_local_supabase_env()
    if not ensure_local_supabase_running(url):
        pytest.skip(
            "Supabase local no está corriendo. Ejecutá "
            "`pnpm --dir frontend supabase:start` "
            "o `docker compose --profile test run --rm integration-tests`."
        )


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
            pytest.skip(
                "La tabla public.users no existe. Aplicá las migraciones de "
                "supabase/migrations en el stack local."
            )
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
