from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from config.instagram_settings import InstagramSettings
from core.instagram.infrastructure.error_infrastructure import TokenDecryptError
from core.shared.infrastructure.versioned_aead import open_sealed, seal


class TokenCrypto:
    def __init__(self, settings: InstagramSettings) -> None:
        self._aes = AESGCM(settings.token_encryption_key_bytes)

    def encrypt(self, token: str, *, associated_data: str) -> str:
        return seal(self._aes, token.encode("utf-8"), associated_data)

    def decrypt(self, encrypted: str, *, associated_data: str) -> str:
        try:
            decrypted = open_sealed(self._aes, encrypted, associated_data)
        except (InvalidTag, ValueError) as exc:
            raise TokenDecryptError("No se pudo leer el token de Instagram") from exc
        return decrypted.decode("utf-8")
