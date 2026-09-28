from datetime import UTC, datetime, timedelta

import pytest

from core.auth.domain.auth_created_at import AuthCreatedAt
from core.shared.domain.domain_error import InvalidDateError


class TestAuthCreatedAt:

    def test_should_create_valid_date(self):
        value = datetime(2026, 9, 12, 12, 0, 0, tzinfo=UTC)

        created_at = AuthCreatedAt(value)

        assert created_at.value == value

    def test_should_reject_invalid_date(self):
        with pytest.raises(InvalidDateError):
            AuthCreatedAt("not a date")

    def test_should_reject_naive_date(self):
        with pytest.raises(InvalidDateError):
            AuthCreatedAt(datetime(2026, 9, 12, 12, 0, 0))

    def test_should_create_current_date_in_utc(self):
        created_at = AuthCreatedAt.now()

        assert created_at.value.utcoffset() == timedelta(0)

    def test_should_create_date_from_isoformat(self):
        value = "2026-09-12T12:00:00+00:00"

        created_at = AuthCreatedAt.from_isoformat(value)

        assert created_at.to_isoformat() == value

    def test_should_reject_naive_isoformat(self):
        with pytest.raises(InvalidDateError):
            AuthCreatedAt.from_isoformat("2026-09-12T12:00:00")
