from datetime import datetime

import pytest

from core.comment.domain.comment_created_at import CommentCreatedAt
from core.shared.domain.domain_error import InvalidDateError


class TestCommentCreatedAt:

    def test_should_create_valid_date(self):
        value = datetime(2026, 9, 22, 12, 0, 0)

        created_at = CommentCreatedAt(value)

        assert created_at.value == value

    def test_should_reject_invalid_date(self):
        with pytest.raises(InvalidDateError):
            CommentCreatedAt("not a date")

    def test_should_create_current_date(self):
        created_at = CommentCreatedAt.now()

        assert created_at is not None

    def test_should_create_date_from_isoformat(self):
        value = "2026-09-22T12:00:00"

        created_at = CommentCreatedAt.from_isoformat(value)

        assert created_at.to_isoformat() == value
