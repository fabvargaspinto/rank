from core.user.application.application_error import (
    InvalidAvatarFileError,
    UserNotFoundError,
)
from core.user.domain.avatar_storage import AvatarStorage
from core.user.domain.user_repo import UserRepository

ALLOWED_AVATAR_TYPES = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
}
MAX_AVATAR_BYTES = 2 * 1024 * 1024


class UploadAvatar:
    def __init__(
        self,
        user_repo: UserRepository,
        avatar_storage: AvatarStorage,
    ):
        self.user_repo = user_repo
        self.avatar_storage = avatar_storage

    def execute(
        self,
        auth_id: str,
        content: bytes,
        content_type: str,
    ) -> str:
        user = self.user_repo.get_user_by_auth_id(auth_id)
        if user is None:
            raise UserNotFoundError("El usuario no existe")

        normalized_type = (content_type or "").split(";")[0].strip().lower()
        if normalized_type not in ALLOWED_AVATAR_TYPES:
            raise InvalidAvatarFileError("La imagen debe ser JPEG, PNG o WebP")

        if not content:
            raise InvalidAvatarFileError("La imagen es inválida")

        if len(content) > MAX_AVATAR_BYTES:
            raise InvalidAvatarFileError("La imagen no puede superar 2 MB")

        return self.avatar_storage.upload(auth_id, content, normalized_type)
