import pytest

from core.user.application.application_error import (
    InvalidAvatarFileError,
    UserNotFoundError,
)
from core.user.application.upload_avatar import MAX_AVATAR_BYTES, UploadAvatar
from core.user.domain.user import User
from tests.unit.user.application.fake_avatar_storage import FakeAvatarStorage
from tests.unit.user.application.fake_user_repo import FakeUserRepo

AUTH_ID = "660e8400-e29b-41d4-a716-446655440000"


class TestUploadAvatar:
    def setup_method(self):
        self.repo = FakeUserRepo()
        self.storage = FakeAvatarStorage()
        self.use_case = UploadAvatar(self.repo, self.storage)
        self.repo.users_by_auth_id[AUTH_ID] = User.create_empty()

    def test_uploads_valid_jpeg(self):
        content = b"\xff\xd8jpeg-bytes"

        url = self.use_case.execute(AUTH_ID, content, "image/jpeg")

        assert url == self.storage.url
        assert self.storage.uploads == [(AUTH_ID, content, "image/jpeg")]

    def test_normalizes_content_type_with_charset(self):
        self.use_case.execute(AUTH_ID, b"png-bytes", "image/png; charset=binary")

        assert self.storage.uploads[0][2] == "image/png"

    def test_raises_when_user_is_missing(self):
        self.repo.users_by_auth_id.clear()

        with pytest.raises(UserNotFoundError, match="El usuario no existe"):
            self.use_case.execute(AUTH_ID, b"jpeg", "image/jpeg")

    def test_rejects_unsupported_type(self):
        with pytest.raises(InvalidAvatarFileError, match="JPEG, PNG o WebP"):
            self.use_case.execute(AUTH_ID, b"gif", "image/gif")

    def test_rejects_empty_file(self):
        with pytest.raises(InvalidAvatarFileError, match="inválida"):
            self.use_case.execute(AUTH_ID, b"", "image/jpeg")

    def test_rejects_oversized_file(self):
        content = b"x" * (MAX_AVATAR_BYTES + 1)

        with pytest.raises(InvalidAvatarFileError, match="2 MB"):
            self.use_case.execute(AUTH_ID, content, "image/jpeg")
