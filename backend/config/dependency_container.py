from functools import lru_cache

from config.crypto_setings import CryptoSettings
from config.db_settings import DBSettings
from core.auth.application.ensure_user_provisioned import EnsureUserProvisioned
from core.auth.application.provision_oauth_user import ProvisionOAuthUser
from core.auth.application.register_with_email import RegisterWithEmail
from core.auth.infrastructure.auth_supabase_repo import AuthSupabaseRepo
from core.auth.infrastructure.email_crypto import EmailCrypto
from db.db_client import DBClient


class DependencyContainer:
    def __init__(self) -> None:
        self.db_settings = DBSettings()  # type: ignore[call-arg]
        self.crypto_settings = CryptoSettings()  # type: ignore[call-arg]
        self.db_client = DBClient(self.db_settings)
        self.email_crypto = EmailCrypto(self.crypto_settings)
        self.auth_repository = AuthSupabaseRepo(self.db_client, self.email_crypto)
        self.register_with_email = RegisterWithEmail(self.auth_repository)
        self.provision_oauth_user = ProvisionOAuthUser(self.auth_repository)

    def ensure_user_provisioned(self) -> EnsureUserProvisioned:
        return EnsureUserProvisioned(
            self.auth_repository,
            self.register_with_email,
            self.provision_oauth_user,
        )


@lru_cache
def get_dependency_container() -> DependencyContainer:
    return DependencyContainer()


def get_ensure_user_provisioned() -> EnsureUserProvisioned:
    return get_dependency_container().ensure_user_provisioned()
