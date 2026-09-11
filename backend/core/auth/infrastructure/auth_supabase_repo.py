
from core.auth.domain.auth_repo import AuthRepository
from core.auth.domain.email_crypto import EmailCrypto
from db.db_client import DBClient


class AuthSupabaseRepo(AuthRepository):
    def __init__(self, db_client: DBClient, email_crypto: EmailCrypto):
        self.db_client = db_client
        self.email_crypto = email_crypto
        self.table = "auth"
        self.providers_table = "auth_providers"

  