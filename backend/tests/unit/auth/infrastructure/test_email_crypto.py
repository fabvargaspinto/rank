import pytest

from config.crypto_setings import CryptoSettings
from core.auth.domain.auth_email import AuthEmail
from core.auth.infrastructure.email_crypto import EmailCrypto
from core.auth.infrastructure.error_infrastructure import EmailDecryptError


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

    assert crypto.decrypt(crypto.encrypt(email)) == email


def test_decrypt_with_another_key_is_an_infrastructure_error():
    encrypted = _crypto("00" * 32).encrypt(AuthEmail("luna@example.com"))

    with pytest.raises(EmailDecryptError, match="No se pudo leer el email"):
        _crypto("22" * 32).decrypt(encrypted)
