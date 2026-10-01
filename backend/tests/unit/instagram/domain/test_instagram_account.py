from datetime import UTC, datetime, timedelta

import pytest

from core.instagram.domain.errors import (
    InvalidFollowersCountError,
    InvalidInstagramAccountIdError,
    InvalidInstagramUsernameError,
    SnapshotWeekMismatchError,
)
from core.instagram.domain.follower_snapshot import FollowerSnapshot
from core.instagram.domain.instagram_account import InstagramAccount
from core.instagram.domain.instagram_connection import InstagramConnection
from core.shared.domain.domain_error import InvalidDateError, InvalidUUIDError

OWNER_ID = "550e8400-e29b-41d4-a716-446655440000"
ACCOUNT_ID = "17841400000000000"
USERNAME = "luna.reyes"
TOKEN_EXPIRES_AT = datetime(2026, 11, 30, 12, 0, tzinfo=UTC)


class TestInstagramAccount:
    def test_creates_account_from_meta_id_and_username(self):
        account = InstagramAccount.create(
            ACCOUNT_ID,
            f"@{USERNAME}",
            "https://scontent.cdninstagram.com/v/t51.2885-19/avatar.jpg",
        )

        assert account.id.value == ACCOUNT_ID
        assert account.username.value == USERNAME
        assert account.avatar_url is not None
        assert account.avatar_url.value.endswith("/avatar.jpg")

    def test_username_is_not_the_identity(self):
        original = InstagramAccount.create(ACCOUNT_ID, USERNAME)
        renamed = original.with_username("luna.nueva")

        assert renamed.id == original.id
        assert renamed.username.value == "luna.nueva"

    def test_rejects_blank_account_id(self):
        with pytest.raises(InvalidInstagramAccountIdError):
            InstagramAccount.create("  ", USERNAME)

    def test_rejects_blank_username(self):
        with pytest.raises(InvalidInstagramUsernameError):
            InstagramAccount.create(ACCOUNT_ID, "   ")

    def test_rejects_non_https_avatar_url(self):
        from core.instagram.domain.errors import InvalidInstagramAvatarUrlError

        with pytest.raises(InvalidInstagramAvatarUrlError):
            InstagramAccount.create(ACCOUNT_ID, USERNAME, "http://example.com/a.jpg")


class TestInstagramConnection:
    def test_connects_account_to_external_owner(self):
        connection = InstagramConnection.connect(
            OWNER_ID,
            ACCOUNT_ID,
            USERNAME,
            TOKEN_EXPIRES_AT,
        )

        assert connection.owner_user_id.value == OWNER_ID
        assert connection.account.id.value == ACCOUNT_ID
        assert connection.account.username.value == USERNAME
        assert connection.belongs_to(OWNER_ID) is True
        assert connection.belongs_to("660e8400-e29b-41d4-a716-446655440000") is False

    def test_rejects_owner_that_is_not_a_uuid(self):
        with pytest.raises(InvalidUUIDError):
            InstagramConnection.connect(
                "not-a-uuid",
                ACCOUNT_ID,
                USERNAME,
                TOKEN_EXPIRES_AT,
            )

    def test_reauthorize_keeps_id_and_owner(self):
        connection = InstagramConnection.connect(
            OWNER_ID,
            ACCOUNT_ID,
            USERNAME,
            TOKEN_EXPIRES_AT,
        )

        next_expiry = datetime(2026, 12, 31, tzinfo=UTC)
        updated = connection.reauthorize("17841499999999999", "otra.cuenta", next_expiry)

        assert updated.id == connection.id
        assert updated.owner_user_id == connection.owner_user_id
        assert updated.created_at == connection.created_at
        assert updated.account.id.value == "17841499999999999"
        assert updated.account.username.value == "otra.cuenta"
        assert updated.token_expires_at.value == next_expiry
        assert updated.updated_at.value > connection.updated_at.value

    def test_token_is_expired_at_expiry_instant(self):
        connection = InstagramConnection.connect(
            OWNER_ID,
            ACCOUNT_ID,
            USERNAME,
            TOKEN_EXPIRES_AT,
        )

        assert connection.token_is_expired(TOKEN_EXPIRES_AT) is True
        assert connection.token_is_expired(TOKEN_EXPIRES_AT - timedelta(seconds=1)) is False


class TestFollowerSnapshot:
    def test_derives_week_start_from_capture_time(self):
        captured_at = datetime(2026, 10, 7, 15, 30, tzinfo=UTC)

        snapshot = FollowerSnapshot.capture(ACCOUNT_ID, 1250, captured_at)

        assert snapshot.followers_count.value == 1250
        assert snapshot.instagram_account_id.value == ACCOUNT_ID
        assert snapshot.week_start.value.isoformat() == "2026-10-05"
        assert snapshot.captured_at.value == captured_at

    def test_sunday_belongs_to_the_same_week(self):
        snapshot = FollowerSnapshot.capture(
            ACCOUNT_ID,
            1280,
            datetime(2026, 10, 11, 23, 0, tzinfo=UTC),
        )

        assert snapshot.week_start.value.isoformat() == "2026-10-05"

    def test_next_monday_is_a_new_week(self):
        first = FollowerSnapshot.capture(
            ACCOUNT_ID,
            1250,
            datetime(2026, 10, 11, 12, 0, tzinfo=UTC),
        )
        second = FollowerSnapshot.capture(
            ACCOUNT_ID,
            1280,
            datetime(2026, 10, 12, 0, 0, tzinfo=UTC),
        )

        assert first.same_week_as(second) is False
        assert second.week_start.value.isoformat() == "2026-10-12"

    def test_two_captures_in_the_same_week_share_the_period(self):
        first = FollowerSnapshot.capture(
            ACCOUNT_ID,
            1250,
            datetime(2026, 10, 5, 9, 0, tzinfo=UTC),
        )
        second = FollowerSnapshot.capture(
            ACCOUNT_ID,
            1260,
            datetime(2026, 10, 8, 18, 0, tzinfo=UTC),
        )

        assert first.same_week_as(second) is True

    def test_replace_count_keeps_id_and_week(self):
        original = FollowerSnapshot.capture(
            ACCOUNT_ID,
            1250,
            datetime(2026, 10, 5, 9, 0, tzinfo=UTC),
        )

        updated = original.replace_count(
            1260,
            datetime(2026, 10, 6, 12, 0, tzinfo=UTC),
        )

        assert updated.id == original.id
        assert updated.week_start == original.week_start
        assert updated.followers_count.value == 1260

    def test_replace_count_rejects_a_different_week(self):
        original = FollowerSnapshot.capture(
            ACCOUNT_ID,
            1250,
            datetime(2026, 10, 5, 9, 0, tzinfo=UTC),
        )

        with pytest.raises(SnapshotWeekMismatchError):
            original.replace_count(
                1300,
                datetime(2026, 10, 12, 9, 0, tzinfo=UTC),
            )

    def test_rejects_negative_followers(self):
        with pytest.raises(InvalidFollowersCountError):
            FollowerSnapshot.capture(ACCOUNT_ID, -1)

    def test_rejects_boolean_followers(self):
        with pytest.raises(InvalidFollowersCountError):
            FollowerSnapshot.capture(ACCOUNT_ID, True)  # type: ignore[arg-type]

    def test_rejects_naive_capture_time(self):
        with pytest.raises(InvalidDateError):
            FollowerSnapshot.capture(
                ACCOUNT_ID,
                100,
                datetime(2026, 10, 5, 9, 0),
            )
