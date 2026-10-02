import hashlib
import hmac

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from config.crypto_settings import CryptoSettings
from core.auth.domain.auth_email import AuthEmail
from core.auth.infrastructure.error_infrastructure import EmailDecryptError
from core.shared.infrastructure.versioned_aead import open_sealed, seal


class EmailCrypto:
    def __init__(
        self,
        crypto_settings: CryptoSettings,
    ):
        self._aes = AESGCM(crypto_settings.email_encryption_key_bytes)
        self._hmac_key = crypto_settings.email_hmac_key_bytes

    def encrypt(self, email: AuthEmail, *, associated_data: str) -> str:
        return seal(self._aes, email.value.encode("utf-8"), associated_data)

    def decrypt(self, encrypted_email: str, *, associated_data: str) -> AuthEmail:
        try:
            decrypted = open_sealed(self._aes, encrypted_email, associated_data)
        except (InvalidTag, ValueError) as exc:
            raise EmailDecryptError("No se pudo leer el email") from exc

        return AuthEmail(decrypted.decode("utf-8"))

    def hmac(self, email: AuthEmail) -> str:
        return hmac.new(
            self._hmac_key,
            email.value.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
