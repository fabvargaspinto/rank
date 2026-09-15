import pytest

from core.user.domain.user_description import UserDescription
from core.user.domain.user_error import InvalidUserDescriptionError


class TestUserDescription:

    def test_should_create_valid_description(self):
        description = UserDescription("My description")

        assert description.value == "My description"

    def test_should_allow_empty_description(self):
        description = UserDescription("")

        assert description.value == ""

    def test_should_accept_description_with_exactly_250_characters(self):
        value = "a" * 250

        description = UserDescription(value)

        assert len(description.value) == 250

    def test_should_reject_description_longer_than_250_characters(self):
        value = "a" * 251

        with pytest.raises(InvalidUserDescriptionError):
            UserDescription(value)

    def test_should_strip_external_spaces(self):
        description = UserDescription("  My description  ")

        assert description.value == "My description"

    def test_should_preserve_internal_spaces(self):
        description = UserDescription("My awesome description")

        assert description.value == "My awesome description"
