import pytest

from core.auth.domain.auth_id import AuthId
from core.shared.domain.domain_error import InvalidUUIDError


class TestAuthId:

    def test_should_create_auth_id(self):
        value = "550e8400-e29b-41d4-a716-446655440000"

        auth_id = AuthId(value)

        assert auth_id.value == value

    def test_should_reject_garbage(self):
        with pytest.raises(InvalidUUIDError):
            AuthId("garbage")
