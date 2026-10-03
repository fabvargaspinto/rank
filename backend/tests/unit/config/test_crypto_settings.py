import pytest
from pydantic import ValidationError

from config.crypto_settings import CryptoSettings


def test_rejects_empty_email_hmac_key():
    with pytest.raises(ValidationError):
        CryptoSettings(
            email_encryption_key="00" * 32,
            email_hmac_key="",
        )


def test_rejects_malformed_email_encryption_key():
    with pytest.raises(ValidationError):
        CryptoSettings(
            email_encryption_key="zz" * 32,
            email_hmac_key="11" * 32,
        )


def test_accepts_valid_hex_keys():
    settings = CryptoSettings(
        email_encryption_key="00" * 32,
        email_hmac_key="11" * 32,
    )

    assert len(settings.email_encryption_key_bytes) == 32
    assert len(settings.email_hmac_key_bytes) == 32
