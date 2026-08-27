import hashlib
import hmac

from cryptography.fernet import Fernet, InvalidToken

from config.crypto_config import CryptoConfig
from core.auth.domain.auth_email import Email
from core.share.infraestructure.infra_error import EmailProtectorError


class FernetEmailProtector:
    def __init__(self, config: CryptoConfig) -> None:
        self._fernet = Fernet(config.email_fernet_key.encode())
        self._hmac_key = config.email_hmac_key.encode()

    def encrypt(self, email: Email) -> str:
        return self._fernet.encrypt(email.value.encode()).decode()

    def decrypt(self, token: str) -> Email:
        try:
            plaintext = self._fernet.decrypt(token.encode()).decode()
        except (InvalidToken, ValueError, TypeError) as error:
            raise EmailProtectorError("Invalid email token") from error
        return Email(plaintext)

    def generate_email_hmac_identifier(self, email: Email) -> str:
        return hmac.new(
            self._hmac_key,
            email.value.encode(),
            hashlib.sha256,
        ).hexdigest()
