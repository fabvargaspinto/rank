from datetime import UTC, datetime, timedelta

import pytest

from config.instagram_settings import InstagramSettings
from core.instagram.application.application_error import InstagramOAuthStateError
from core.instagram.domain.oauth_state import InstagramOAuthState
from core.instagram.infrastructure.error_infrastructure import TokenDecryptError
from core.instagram.infrastructure.oauth_state_codec import SignedOAuthStateCodec
from core.instagram.infrastructure.token_crypto import TokenCrypto

OWNER_ID = "550e8400-e29b-41d4-a716-446655440000"


def _settings(key: str = "00" * 32) -> InstagramSettings:
    return InstagramSettings(
        instagram_app_id="123456",
        instagram_app_secret="app-secret",
        instagram_redirect_uri="http://localhost:8000/instagram/oauth/callback",
        instagram_token_encryption_key=key,
        frontend_url="http://localhost:3000",
    )


def test_token_round_trip():
    crypto = TokenCrypto(_settings())

    assert crypto.decrypt(crypto.encrypt("ig-secret-token")) == "ig-secret-token"


def test_token_decrypt_with_another_key_fails():
    encrypted = TokenCrypto(_settings("00" * 32)).encrypt("ig-secret-token")

    with pytest.raises(TokenDecryptError):
        TokenCrypto(_settings("22" * 32)).decrypt(encrypted)


def test_oauth_state_round_trip():
    codec = SignedOAuthStateCodec(_settings())
    now = datetime(2026, 10, 5, 12, 0, tzinfo=UTC)
    state = InstagramOAuthState.issue(OWNER_ID, "nonce-1", now)

    loaded = codec.loads(codec.dumps(state))

    assert loaded.owner_user_id.value == OWNER_ID
    assert loaded.nonce == "nonce-1"
    assert loaded.expires_at == now + timedelta(minutes=10)


def test_oauth_state_rejects_tampering():
    codec = SignedOAuthStateCodec(_settings())
    state = InstagramOAuthState.issue(
        OWNER_ID,
        "nonce-1",
        datetime(2026, 10, 5, 12, 0, tzinfo=UTC),
    )
    token = codec.dumps(state)

    with pytest.raises(InstagramOAuthStateError):
        codec.loads(token + "x")
