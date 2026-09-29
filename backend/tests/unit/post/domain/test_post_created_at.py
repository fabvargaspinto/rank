from datetime import UTC, datetime

import pytest

from core.post.domain.post_created_at import PostCreatedAt
from core.shared.domain.domain_error import InvalidDateError


class TestPostCreatedAt:

    def test_should_create_valid_date(self):
        value = datetime(2026, 9, 22, 12, 0, 0, tzinfo=UTC)

        created_at = PostCreatedAt(value)

        assert created_at.value == value

    def test_should_reject_invalid_date(self):
        with pytest.raises(InvalidDateError):
            PostCreatedAt("not a date")

    def test_should_reject_naive_date(self):
        with pytest.raises(InvalidDateError):
            PostCreatedAt(datetime(2026, 9, 22, 12, 0, 0))

    def test_should_create_current_date(self):
        created_at = PostCreatedAt.now()

        assert created_at.value.utcoffset() is not None

    def test_should_create_date_from_isoformat(self):
        value = "2026-09-22T12:00:00+00:00"

        created_at = PostCreatedAt.from_isoformat(value)

        assert created_at.to_isoformat() == value
