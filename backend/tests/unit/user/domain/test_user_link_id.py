import pytest

from core.shared.domain.domain_error import InvalidUUIDError
from core.user.domain.user_link_id import UserLinkId


class TestUserLinkId:

    def test_should_create_user_link_id(self):
        value = "550e8400-e29b-41d4-a716-446655440000"

        link_id = UserLinkId(value)

        assert link_id.value == value

    def test_should_reject_invalid_uuid(self):
        with pytest.raises(InvalidUUIDError):
            UserLinkId("NOT-A-UUID")

    def test_should_generate_user_link_id(self):
        link_id = UserLinkId.generate()

        assert link_id is not None
        assert link_id.value is not None

    def test_should_generate_different_ids(self):
        first_id = UserLinkId.generate()
        second_id = UserLinkId.generate()

        assert first_id != second_id
