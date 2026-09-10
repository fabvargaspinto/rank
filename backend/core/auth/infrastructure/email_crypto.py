import hashlib
import hmac
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from config.bootstrap import Bootstrap
from core.auth.domain.auth_email import AuthEmail


class EmailCrypto:
    def __init__(
        self,
        bootstrap: Bootstrap,
    ):
        self._aes = AESGCM(bootstrap.email_encryption_key_bytes)
        self._hmac_key = bootstrap.email_hmac_key_bytes

    def encrypt(self, email: AuthEmail) -> str:
        nonce = os.urandom(12)

        encrypted = self._aes.encrypt(
            nonce,
            email.value.encode("utf-8"),
            None,
        )

        return (nonce + encrypted).hex()

    def decrypt(self, encrypted_email: str) -> AuthEmail:
        data = bytes.fromhex(encrypted_email)

        nonce = data[:12]
        ciphertext = data[12:]

        decrypted = self._aes.decrypt(
            nonce,
            ciphertext,
            None,
        )

        return AuthEmail(decrypted.decode("utf-8"))

    def hmac(self, email: AuthEmail) -> str:
        return hmac.new(
            self._hmac_key,
            email.value.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
