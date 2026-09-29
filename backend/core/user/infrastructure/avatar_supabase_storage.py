from storage3.exceptions import StorageApiError

from core.shared.infrastructure.supabase_client import DBClient
from core.user.infrastructure.error_infrastructure import AvatarUploadError

BUCKET = "avatars"


class AvatarSupabaseStorage:
    def __init__(self, client: DBClient):
        self._db = client.get_db()

    def upload(
        self,
        path: str,
        content: bytes,
        content_type: str,
    ) -> None:
        try:
            self._db.storage.from_(BUCKET).upload(
                path,
                content,
                file_options={
                    "content-type": content_type,
                    "upsert": "true",
                    "cache-control": "31536000",
                },
            )
        except StorageApiError as exc:
            raise AvatarUploadError("Error al subir la imagen") from exc
        except Exception as exc:
            raise AvatarUploadError("Error al subir la imagen") from exc

    def delete(self, path: str) -> None:
        try:
            self._db.storage.from_(BUCKET).remove([path])
        except Exception:
            return
