import os

import pytest
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from config.crypto_setings import CryptoSettings
from core.auth.infrastructure.email_crypto import EmailCrypto


@pytest.fixture
def crypto_settings() -> CryptoSettings:
    return CryptoSettings(
        email_encryption_key=AESGCM.generate_key(bit_length=256).hex(),
        email_hmac_key=os.urandom(32).hex(),
    )


@pytest.fixture
def email_crypto(crypto_settings: CryptoSettings) -> EmailCrypto:
    return EmailCrypto(crypto_settings)
