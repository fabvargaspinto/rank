import pytest

from core.user.domain.user_error import InvalidUserAvatarError
from core.user.infrastructure.avatar_url import object_path, public_avatar_url

PATH = "550e8400-e29b-41d4-a716-446655440000/avatar.webp"
BASE = "https://example.supabase.co"


class TestAvatarUrl:
    def test_keeps_an_object_path(self):
        assert object_path(f"  {PATH}  ") == PATH

    def test_extracts_the_path_from_a_public_url(self):
        url = public_avatar_url(BASE, PATH)

        assert object_path(url) == PATH

    def test_rejects_a_foreign_url(self):
        with pytest.raises(InvalidUserAvatarError):
            object_path("https://otro-dominio.example/pixel.gif")

    def test_builds_the_public_url(self):
        assert public_avatar_url(BASE + "/", PATH) == (
            f"{BASE}/storage/v1/object/public/avatars/{PATH}"
        )
