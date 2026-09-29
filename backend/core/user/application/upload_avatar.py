from core.shared.domain.uuid import UUID
from core.user.application.application_error import UserNotFoundError
from core.user.application.avatar_image import recode_avatar
from core.user.domain.avatar_storage import AvatarStorage
from core.user.domain.user import User
from core.user.domain.user_error import UserProfileNotFoundError
from core.user.domain.user_repo import UserRepository

MAX_AVATAR_BYTES = 2 * 1024 * 1024


class UploadAvatar:
    def __init__(
        self,
        user_repo: UserRepository,
        avatar_storage: AvatarStorage,
    ):
        self.user_repo = user_repo
        self.avatar_storage = avatar_storage

    def execute(self, user: User, content: bytes) -> str:
        encoded = recode_avatar(content, MAX_AVATAR_BYTES)
        previous = user.avatar.value if user.avatar else None
        path = f"{user.id.value}/{UUID.generate().value}.webp"
        self.avatar_storage.upload(path, encoded, "image/webp")
        user.change_avatar(path)
        try:
            self.user_repo.save(user)
        except UserProfileNotFoundError as exc:
            raise UserNotFoundError("El usuario no existe") from exc
        if previous and previous != path:
            self.avatar_storage.delete(previous)
        return path
