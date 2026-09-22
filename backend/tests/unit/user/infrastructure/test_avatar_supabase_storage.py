from storage3.exceptions import StorageApiError

from core.user.infrastructure.avatar_supabase_storage import AvatarSupabaseStorage
from core.user.infrastructure.error_infrastructure import AvatarUploadError

AUTH_ID = "660e8400-e29b-41d4-a716-446655440000"


class _FakeBucket:
    def __init__(self, fail: bool = False):
        self.fail = fail
        self.uploads: list[tuple] = []

    def upload(self, path, file, file_options=None):
        if self.fail:
            raise StorageApiError("Access denied", "403", 403)
        self.uploads.append((path, file, file_options))

    def get_public_url(self, path: str) -> str:
        return f"https://example.supabase.co/storage/v1/object/public/avatars/{path}?download="


class _FakeStorage:
    def __init__(self, bucket: _FakeBucket):
        self._bucket = bucket

    def from_(self, _name: str):
        return self._bucket


class _FakeSupabase:
    def __init__(self, bucket: _FakeBucket):
        self.storage = _FakeStorage(bucket)


class _FakeDBClient:
    def __init__(self, bucket: _FakeBucket):
        self._client = _FakeSupabase(bucket)

    def get_db(self):
        return self._client


class TestAvatarSupabaseStorage:
    def test_uploads_to_auth_id_path_and_strips_query(self):
        bucket = _FakeBucket()
        storage = AvatarSupabaseStorage(_FakeDBClient(bucket))

        url = storage.upload(AUTH_ID, b"jpeg-bytes", "image/jpeg")

        assert bucket.uploads[0][0] == f"{AUTH_ID}/avatar.jpg"
        assert bucket.uploads[0][1] == b"jpeg-bytes"
        assert bucket.uploads[0][2]["upsert"] == "true"
        assert bucket.uploads[0][2]["content-type"] == "image/jpeg"
        assert url == (
            "https://example.supabase.co/storage/v1/object/public/"
            f"avatars/{AUTH_ID}/avatar.jpg"
        )

    def test_wraps_storage_errors(self):
        storage = AvatarSupabaseStorage(_FakeDBClient(_FakeBucket(fail=True)))

        try:
            storage.upload(AUTH_ID, b"jpeg-bytes", "image/jpeg")
            raise AssertionError("expected AvatarUploadError")
        except AvatarUploadError as exc:
            assert str(exc) == "Error al subir la imagen"
