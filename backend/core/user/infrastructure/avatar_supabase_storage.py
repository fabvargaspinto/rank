from storage3.exceptions import StorageApiError

from core.user.infrastructure.error_infrastructure import AvatarUploadError
from db.db_client import DBClient

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
                    "cache-control": "3600",
                },
            )
        except StorageApiError as exc:
            raise AvatarUploadError("Error al subir la imagen") from exc
        except Exception as exc:
            raise AvatarUploadError("Error al subir la imagen") from exc

    def delete(self, auth_id: str) -> None:
        try:
            listed = self._db.storage.from_(BUCKET).list(auth_id) or []
            paths = [
                f"{auth_id}/{item['name']}"
                for item in listed
                if isinstance(item, dict) and item.get("name")
            ]
            if paths:
                self._db.storage.from_(BUCKET).remove(paths)
        except Exception:
            return
