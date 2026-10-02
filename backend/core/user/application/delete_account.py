from core.auth.domain.auth_repo import AuthRepository
from core.user.domain.avatar_storage import AvatarStorage
from core.user.domain.user_repo import UserRepository


class DeleteAccount:
    def __init__(
        self,
        user_repo: UserRepository,
        avatar_storage: AvatarStorage,
        auth_repo: AuthRepository,
    ):
        self.user_repo = user_repo
        self.avatar_storage = avatar_storage
        self.auth_repo = auth_repo

    def execute(self, auth_id: str) -> None:
        user = self.user_repo.get_user_by_auth_id(auth_id)
        if user is not None:
            if user.avatar is not None and user.avatar.belongs_to(user.id):
                self.avatar_storage.delete(user.avatar.value)
            self.user_repo.delete_user(user.id.value)
        self.auth_repo.delete_identity(auth_id)
