import pytest

from core.user.domain.user_error import InvalidUserNameError
from core.user.domain.user_name import UserName


class TestUserName:
    def test_normalizes_before_comparing(self):
        assert UserName("  Luna ").value == "luna"
        assert UserName("  Luna ") == UserName("luna")
        assert UserName("Fab") == UserName("fab")
        assert UserName("Laura") == UserName("lAura")
        assert UserName("Laura").value == "laura"
        assert hash(UserName("Fab")) == hash(UserName("fab"))

    def test_accepts_letters_numbers_and_separators(self):
        assert UserName("luna.reyes").value == "luna.reyes"
        assert UserName("Dj_Nova-1").value == "dj_nova-1"

    def test_accepts_3_and_30_characters(self):
        assert UserName("abc").value == "abc"
        assert len(UserName("a" * 30).value) == 30

    def test_rejects_display_names_reserved_words_and_emoji(self):
        for value in ("Luna Reyes", "login", "\U0001F3B8\U0001F3B8", "ab", "a" * 31):
            with pytest.raises(InvalidUserNameError):
                UserName(value)

    def test_rejects_routes_that_would_hide_the_profile(self):
        for value in ("Login", "robots.txt", "sitemap.xml", "favicon.ico", "dashboard"):
            with pytest.raises(InvalidUserNameError):
                UserName(value)

    def test_rejects_missing_value(self):
        with pytest.raises(InvalidUserNameError):
            UserName("")

        with pytest.raises(InvalidUserNameError):
            UserName("   ")

        with pytest.raises(InvalidUserNameError):
            UserName(None)  # type: ignore[arg-type]
