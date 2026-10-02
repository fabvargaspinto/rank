import os

import pytest
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from config.crypto_settings import CryptoSettings
from core.auth.domain.auth_email import AuthEmail
from core.auth.infrastructure.email_crypto import EmailCrypto
from core.auth.infrastructure.error_infrastructure import EmailDecryptError

AUTH_ID = "550e8400-e29b-41d4-a716-446655440000"


def _crypto(encryption_key: str) -> EmailCrypto:
    return EmailCrypto(
        CryptoSettings(
            email_encryption_key=encryption_key,
            email_hmac_key="11" * 32,
        )
    )


def test_decrypt_round_trip():
    crypto = _crypto("00" * 32)
    email = AuthEmail("luna@example.com")

    sealed = crypto.encrypt(email, associated_data=AUTH_ID)

    assert sealed.startswith("v1:")
    assert crypto.decrypt(sealed, associated_data=AUTH_ID) == email


def test_decrypt_rejects_wrong_associated_data():
    crypto = _crypto("00" * 32)
    sealed = crypto.encrypt(AuthEmail("luna@example.com"), associated_data=AUTH_ID)

    with pytest.raises(EmailDecryptError, match="No se pudo leer el email"):
        crypto.decrypt(sealed, associated_data="other-id")


def test_decrypt_with_another_key_is_an_infrastructure_error():
    encrypted = _crypto("00" * 32).encrypt(
        AuthEmail("luna@example.com"),
        associated_data=AUTH_ID,
    )

    with pytest.raises(EmailDecryptError, match="No se pudo leer el email"):
        _crypto("22" * 32).decrypt(encrypted, associated_data=AUTH_ID)


def test_decrypt_legacy_ciphertext_without_prefix():
    key = bytes.fromhex("00" * 32)
    aes = AESGCM(key)
    nonce = os.urandom(12)
    legacy = (nonce + aes.encrypt(nonce, b"luna@example.com", None)).hex()

    assert (
        _crypto("00" * 32).decrypt(legacy, associated_data=AUTH_ID).value
        == "luna@example.com"
    )
