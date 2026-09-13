from functools import lru_cache

from config.crypto_setings import CryptoSettings
from config.db_settings import DBSettings
from core.auth.application.ensure_user_provisioned import EnsureUserProvisioned
from core.auth.infrastructure.auth_supabase_repo import AuthSupabaseRepo
from core.auth.infrastructure.email_crypto import EmailCrypto
from db.db_client import DBClient


class DependencyContainer:
    def __init__(self) -> None:
        self.db_settings = DBSettings()
        self.crypto_settings = CryptoSettings()
        self.db_client = DBClient(self.db_settings)
        self.email_crypto = EmailCrypto(self.crypto_settings)
        self.auth_repository = AuthSupabaseRepo(self.db_client, self.email_crypto)

    def ensure_user_provisioned(self) -> EnsureUserProvisioned:
        return EnsureUserProvisioned(self.auth_repository)


@lru_cache
def get_dependency_container() -> DependencyContainer:
    return DependencyContainer()


def get_ensure_user_provisioned() -> EnsureUserProvisioned:
    return get_dependency_container().ensure_user_provisioned()
