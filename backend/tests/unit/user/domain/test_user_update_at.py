from datetime import datetime

import pytest

from core.shared.domain.domain_error import InvalidDateError
from core.user.domain.user_updated_at import UserUpdatedAt

# TODO: hacer un clock mock para testear el updated_at

class TestUserUpdatedAt:

    def test_should_create_valid_date(self):
        value = datetime(2026, 9, 12, 12, 0, 0)

        updated_at = UserUpdatedAt(value)

        assert updated_at.value == value

    def test_should_reject_invalid_date(self):
        with pytest.raises(InvalidDateError):
            UserUpdatedAt("not a date")

    def test_should_create_current_date(self):
        updated_at = UserUpdatedAt.now()

        assert updated_at is not None

    def test_should_create_date_from_isoformat(self):
        value = "2026-09-12T12:00:00"

        updated_at = UserUpdatedAt.from_isoformat(value)

        assert updated_at.to_isoformat() == value