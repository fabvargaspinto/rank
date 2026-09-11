from functools import lru_cache

from config.crypto_setings import CryptoSettings
from config.db_settings import DBSettings
from core.auth.application.login_user import LoginUserUseCase
from core.auth.application.register_user import RegisterUserUseCase
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

    def register_user_use_case(self) -> RegisterUserUseCase:
        return RegisterUserUseCase(self.auth_repository)

    def login_user_use_case(self) -> LoginUserUseCase:
        return LoginUserUseCase(self.auth_repository)


@lru_cache
def get_dependency_container() -> DependencyContainer:
    return DependencyContainer()
