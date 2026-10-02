import pytest

from config.crypto_settings import CryptoSettings
from core.auth.infrastructure.auth_supabase_repo import AuthSupabaseRepo
from core.auth.infrastructure.email_crypto import EmailCrypto
from core.auth.infrastructure.error_infrastructure import AuthLookupError


class _FailingQuery:
    def select(self, *_args, **_kwargs):
        return self

    def eq(self, *_args, **_kwargs):
        return self

    def limit(self, *_args, **_kwargs):
        return self

    def execute(self):
        raise RuntimeError("db down")


class _FailingDB:
    def table(self, _name: str):
        return _FailingQuery()


class _FailingClient:
    def get_db(self):
        return _FailingDB()


def test_find_by_id_wraps_lookup_failures():
    repo = AuthSupabaseRepo(
        _FailingClient(),
        EmailCrypto(
            CryptoSettings(
                email_encryption_key="00" * 32,
                email_hmac_key="11" * 32,
            )
        ),
    )

    with pytest.raises(AuthLookupError, match="Error al buscar el usuario"):
        repo.find_by_id("660e8400-e29b-41d4-a716-446655440000")
