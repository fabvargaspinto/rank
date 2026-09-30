import os

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from config.instagram_settings import InstagramSettings
from core.instagram.infrastructure.error_infrastructure import TokenDecryptError


class TokenCrypto:
    def __init__(self, settings: InstagramSettings) -> None:
        self._aes = AESGCM(settings.token_encryption_key_bytes)

    def encrypt(self, token: str) -> str:
        nonce = os.urandom(12)
        encrypted = self._aes.encrypt(nonce, token.encode("utf-8"), None)
        return (nonce + encrypted).hex()

    def decrypt(self, encrypted: str) -> str:
        data = bytes.fromhex(encrypted)
        nonce = data[:12]
        ciphertext = data[12:]
        try:
            decrypted = self._aes.decrypt(nonce, ciphertext, None)
        except InvalidTag as exc:
            raise TokenDecryptError("No se pudo leer el token de Instagram") from exc
        return decrypted.decode("utf-8")
