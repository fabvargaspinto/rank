import pytest

from core.user.domain.user_display_name import UserDisplayName
from core.user.domain.user_error import InvalidUserDisplayNameError


class TestUserDisplayName:
    def test_keeps_accents_spaces_and_emoji(self):
        name = UserDisplayName("  Luna Reyes 🎸 ")

        assert name.value == "Luna Reyes 🎸"

    def test_accepts_50_characters(self):
        assert len(UserDisplayName("á" * 50).value) == 50

    def test_rejects_empty_and_too_long(self):
        with pytest.raises(InvalidUserDisplayNameError):
            UserDisplayName("   ")

        with pytest.raises(InvalidUserDisplayNameError):
            UserDisplayName("a" * 51)
