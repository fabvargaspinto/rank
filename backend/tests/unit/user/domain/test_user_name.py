from pathlib import Path

import pytest

from core.user.domain.user_error import InvalidUserNameError
from core.user.domain.user_name import UserName

_REPO_ROOT = Path(__file__).resolve().parents[5]
_APP_DIR = _REPO_ROOT / "frontend" / "app"

_FRAMEWORK_STEMS = frozenset(
    {
        "page",
        "layout",
        "loading",
        "error",
        "global-error",
        "not-found",
        "template",
        "default",
        "route",
    }
)
_SPECIAL_STEMS = {
    "robots": "robots.txt",
    "sitemap": "sitemap.xml",
    "icon": "icon",
    "apple-icon": "apple-icon",
    "opengraph-image": "opengraph-image",
    "twitter-image": "twitter-image",
    "favicon": "favicon.ico",
}
_SKIP_SUFFIXES = (".css", ".scss", ".sass", ".md")


def _first_level_app_segments(app_dir: Path) -> set[str]:
    segments: set[str] = set()

    def walk(directory: Path) -> None:
        for entry in directory.iterdir():
            name = entry.name
            if name.startswith("."):
                continue
            if entry.is_dir():
                if name.startswith("(") and name.endswith(")"):
                    walk(entry)
                elif name.startswith("[") and name.endswith("]"):
                    continue
                else:
                    segments.add(name)
                continue
            if name.endswith(_SKIP_SUFFIXES):
                continue
            stem = name.rsplit(".", 1)[0]
            if stem in _FRAMEWORK_STEMS:
                continue
            segments.add(_SPECIAL_STEMS.get(stem, stem.lower()))

    walk(app_dir)
    return segments


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
        for value in (
            "Login",
            "robots.txt",
            "sitemap.xml",
            "favicon.ico",
            "dashboard",
            "forgot-password",
            "reset-password",
            "icon",
            "opengraph-image",
            "privacidad",
            "terminos",
        ):
            with pytest.raises(InvalidUserNameError):
                UserName(value)

    def test_rejects_missing_value(self):
        with pytest.raises(InvalidUserNameError):
            UserName("")

        with pytest.raises(InvalidUserNameError):
            UserName("   ")

        with pytest.raises(InvalidUserNameError):
            UserName(None)  # type: ignore[arg-type]

    def test_frontend_app_segments_are_reserved(self):
        assert _APP_DIR.is_dir(), f"missing frontend app dir: {_APP_DIR}"
        missing = sorted(_first_level_app_segments(_APP_DIR) - UserName.RESERVED)
        assert missing == [], (
            "First-level frontend/app segments must be in UserName.RESERVED: "
            + ", ".join(missing)
        )

    def test_schema_check_lists_every_reserved_name(self):
        schema = (_REPO_ROOT / "supabase" / "schema.sql").read_text()
        missing = sorted(
            name for name in UserName.RESERVED if f"'{name}'" not in schema
        )
        assert missing == [], (
            "supabase/schema.sql users_name_format must list: "
            + ", ".join(missing)
        )
