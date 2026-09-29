from io import BytesIO

import pytest
from PIL import Image

from core.user.application.application_error import InvalidAvatarFileError
from core.user.application.upload_avatar import MAX_AVATAR_BYTES, UploadAvatar
from core.user.domain.user import User
from tests.unit.user.application.fake_avatar_storage import FakeAvatarStorage
from tests.unit.user.application.fake_user_repo import FakeUserRepo

AUTH_ID = "660e8400-e29b-41d4-a716-446655440000"


def _image_bytes(fmt: str) -> bytes:
    output = BytesIO()
    Image.new("RGB", (8, 8), "red").save(output, format=fmt)
    return output.getvalue()


class TestUploadAvatar:
    def setup_method(self):
        self.repo = FakeUserRepo()
        self.storage = FakeAvatarStorage()
        self.use_case = UploadAvatar(self.repo, self.storage)
        self.user = User.create_empty()
        self.repo.users_by_auth_id[AUTH_ID] = self.user

    def test_recodes_a_jpeg_to_webp_and_saves_the_path(self):
        content = _image_bytes("JPEG")

        path = self.use_case.execute(self.user, AUTH_ID, content)

        assert path == f"{AUTH_ID}/avatar.webp"
        stored_path, stored_bytes, stored_type = self.storage.uploads[0]
        assert stored_path == path
        assert stored_type == "image/webp"
        assert stored_bytes.startswith(b"RIFF")
        assert self.user.avatar is not None
        assert self.user.avatar.value == path

    def test_accepts_png_bytes_even_if_the_name_says_otherwise(self):
        path = self.use_case.execute(self.user, AUTH_ID, _image_bytes("PNG"))

        assert path.endswith("avatar.webp")

    def test_rejects_bytes_that_are_not_an_image(self):
        with pytest.raises(InvalidAvatarFileError, match="inválida"):
            self.use_case.execute(self.user, AUTH_ID, b"png-bytes")

    def test_rejects_gif(self):
        with pytest.raises(InvalidAvatarFileError, match="JPEG, PNG o WebP"):
            self.use_case.execute(self.user, AUTH_ID, _image_bytes("GIF"))

    def test_rejects_empty_file(self):
        with pytest.raises(InvalidAvatarFileError, match="inválida"):
            self.use_case.execute(self.user, AUTH_ID, b"")

    def test_rejects_oversized_file(self):
        content = b"x" * (MAX_AVATAR_BYTES + 1)

        with pytest.raises(InvalidAvatarFileError, match="2 MB"):
            self.use_case.execute(self.user, AUTH_ID, content)
