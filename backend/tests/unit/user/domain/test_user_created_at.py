from datetime import datetime

import pytest

from core.shared.domain.domain_error import InvalidDateError
from core.user.domain.user_created_at import UserCreatedAt

# TODO: hacer un clock mock para testear el created_at

class TestUserCreatedAt:

    def test_should_create_valid_date(self):
        value = datetime(2026, 9, 12, 12, 0, 0)

        created_at = UserCreatedAt(value)

        assert created_at.value == value

    def test_should_reject_invalid_date(self):
        with pytest.raises(InvalidDateError):
            UserCreatedAt("not a date")

    def test_should_create_current_date(self):
        created_at = UserCreatedAt.now()

        assert created_at is not None

    def test_should_create_date_from_isoformat(self):
        value = "2026-09-12T12:00:00"

        created_at = UserCreatedAt.from_isoformat(value)

        assert created_at.to_isoformat() == value
