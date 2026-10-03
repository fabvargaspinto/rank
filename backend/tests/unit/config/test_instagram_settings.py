import pytest
from pydantic import ValidationError

from config.instagram_settings import InstagramSettings

_VALID = {
    "instagram_app_id": "123456",
    "instagram_app_secret": "app-secret",
    "instagram_redirect_uri": "http://localhost:3000/auth/instagram/callback",
    "instagram_token_encryption_key": "00" * 32,
}


def test_rejects_empty_app_secret():
    with pytest.raises(ValidationError):
        InstagramSettings(**{**_VALID, "instagram_app_secret": ""})


def test_rejects_empty_app_id():
    with pytest.raises(ValidationError):
        InstagramSettings(**{**_VALID, "instagram_app_id": ""})


def test_rejects_malformed_token_encryption_key():
    with pytest.raises(ValidationError):
        InstagramSettings(**{**_VALID, "instagram_token_encryption_key": "not-hex"})


def test_accepts_valid_settings():
    settings = InstagramSettings(**_VALID)

    assert settings.instagram_app_secret == "app-secret"
    assert len(settings.token_encryption_key_bytes) == 32
