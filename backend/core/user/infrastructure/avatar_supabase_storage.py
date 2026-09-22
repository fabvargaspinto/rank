from storage3.exceptions import StorageApiError

from core.user.application.upload_avatar import ALLOWED_AVATAR_TYPES
from core.user.infrastructure.error_infrastructure import AvatarUploadError
from db.db_client import DBClient

BUCKET = "avatars"


class AvatarSupabaseStorage:
    def __init__(self, client: DBClient):
        self._db = client.get_db()

    def upload(
        self,
        auth_id: str,
        content: bytes,
        content_type: str,
    ) -> str:
        ext = ALLOWED_AVATAR_TYPES[content_type]
        path = f"{auth_id}/avatar.{ext}"

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

        url = self._db.storage.from_(BUCKET).get_public_url(path)
        return url.split("?")[0]
