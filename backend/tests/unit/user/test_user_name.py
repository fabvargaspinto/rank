import pytest

from core.user.domain.user_name import UserName
from core.user.domain.user_error import InvalidUserNameError


class TestUserName:

    def test_should_create_valid_name(self):
        name = UserName("John")

        assert name.value == "John"

    def test_should_reject_empty_name(self):
        with pytest.raises(InvalidUserNameError):
            UserName("")

    def test_should_accept_name_with_exactly_1_character(self):
        name = UserName("A")

        assert name.value == "A"

    def test_should_accept_name_with_exactly_50_characters(self):
        value = "a" * 50

        name = UserName(value)

        assert len(name.value) == 50

    def test_should_reject_name_longer_than_50_characters(self):
        value = "a" * 51

        with pytest.raises(InvalidUserNameError):
            UserName(value)

    def test_should_strip_external_spaces(self):
        name = UserName("  John  ")

        assert name.value == "John"

    def test_should_preserve_internal_spaces(self):
        name = UserName("John Doe")

        assert name.value == "John Doe"

    def test_should_count_spaces_as_characters(self):
        name = UserName("Juan Pérez")

        assert len(name.value) == 10

    def test_should_reject_name_with_only_spaces(self):
        with pytest.raises(InvalidUserNameError):
            UserName("   ")   