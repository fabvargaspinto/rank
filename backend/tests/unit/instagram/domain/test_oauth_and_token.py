from datetime import UTC, datetime, timedelta

import pytest

from core.instagram.domain.errors import (
    InstagramOAuthStateExpiredError,
    InvalidInstagramTokenError,
    InvalidOAuthNonceError,
)
from core.instagram.domain.instagram_graph import InstagramAccessToken
from core.instagram.domain.oauth_state import InstagramOAuthState

OWNER_ID = "550e8400-e29b-41d4-a716-446655440000"


class TestInstagramOAuthState:
    def test_issues_state_bound_to_owner(self):
        now = datetime(2026, 10, 5, 12, 0, tzinfo=UTC)

        state = InstagramOAuthState.issue(OWNER_ID, "nonce-1", now)

        assert state.owner_user_id.value == OWNER_ID
        assert state.nonce == "nonce-1"
        assert state.expires_at == now + timedelta(minutes=10)
        state.ensure_valid(now)

    def test_expires_at_ttl(self):
        now = datetime(2026, 10, 5, 12, 0, tzinfo=UTC)
        state = InstagramOAuthState.issue(OWNER_ID, "nonce-1", now)

        with pytest.raises(InstagramOAuthStateExpiredError):
            state.ensure_valid(now + timedelta(minutes=10))

    def test_rejects_blank_nonce(self):
        with pytest.raises(InvalidOAuthNonceError):
            InstagramOAuthState.issue(OWNER_ID, "  ")


class TestInstagramAccessToken:
    def test_hides_secret_in_repr_and_str(self):
        token = InstagramAccessToken(
            "IGQWBSECRETTOKEN",
            datetime(2026, 11, 1, tzinfo=UTC),
        )

        assert "IGQWBSECRETTOKEN" not in repr(token)
        assert "IGQWBSECRETTOKEN" not in str(token)
        assert token.value == "IGQWBSECRETTOKEN"

    def test_rejects_blank_token(self):
        with pytest.raises(InvalidInstagramTokenError):
            InstagramAccessToken("  ", datetime(2026, 11, 1, tzinfo=UTC))
