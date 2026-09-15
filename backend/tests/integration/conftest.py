import os

import pytest
from postgrest.exceptions import APIError

from config.crypto_setings import CryptoSettings
from config.db_settings import DBSettings
from core.auth.infrastructure.auth_supabase_repo import AuthSupabaseRepo
from core.auth.infrastructure.email_crypto import EmailCrypto
from db.db_client import DBClient


def _supabase_env_ready() -> bool:
    url = os.getenv("SUPABASE_URL", "").strip()
    key = os.getenv("SUPABASE_SECRET_KEY", "").strip()
    return bool(url and key)


@pytest.fixture(scope="session", autouse=True)
def require_supabase() -> None:
    if not _supabase_env_ready():
        pytest.skip(
            "Supabase no está configurado. Definí SUPABASE_URL y "
            "SUPABASE_SECRET_KEY en el .env de la raíz del repo."
        )


@pytest.fixture(scope="session")
def db_settings() -> DBSettings:
    return DBSettings()


@pytest.fixture(scope="session")
def db_client(db_settings: DBSettings) -> DBClient:
    return DBClient(db_settings)


@pytest.fixture(scope="session")
def users_table(db_client: DBClient):
    try:
        db_client.get_db().table("users").select("id").limit(1).execute()
    except APIError as exc:
        if exc.code == "PGRST205":
            pytest.skip(
                "La tabla public.users no existe. Aplicá backend/db/schema.sql "
                "en el proyecto de Supabase."
            )
        raise
    return db_client


def _anon_key() -> str:
    return (
        os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY", "").strip()
        or os.getenv("SUPABASE_ANON_KEY", "").strip()
    )


@pytest.fixture(scope="session")
def anon_client(db_settings: DBSettings):
    key = _anon_key()
    if not key:
        pytest.skip(
            "Definí NEXT_PUBLIC_SUPABASE_ANON_KEY para probar acceso anon "
            "y autenticado."
        )

    from supabase import ClientOptions, create_client

    return create_client(
        db_settings.supabase_url,
        key,
        options=ClientOptions(
            auto_refresh_token=False,
            persist_session=False,
        ),
    )


def _crypto_env_ready() -> bool:
    return bool(
        os.getenv("EMAIL_ENCRYPTION_KEY", "").strip()
        and os.getenv("EMAIL_HMAC_KEY", "").strip()
    )


@pytest.fixture(scope="session")
def email_crypto() -> EmailCrypto:
    if not _crypto_env_ready():
        pytest.skip(
            "Definí EMAIL_ENCRYPTION_KEY y EMAIL_HMAC_KEY en el .env "
            "de la raíz del repo."
        )
    return EmailCrypto(CryptoSettings())


@pytest.fixture(scope="session")
def auth_repo(users_table: DBClient, email_crypto: EmailCrypto) -> AuthSupabaseRepo:
    return AuthSupabaseRepo(users_table, email_crypto)
