from functools import lru_cache

from config.crypto_setings import CryptoSettings
from config.db_settings import DBSettings
from core.auth.application.provision_identity import ProvisionIdentity
from core.auth.infrastructure.auth_supabase_repo import AuthSupabaseRepo
from core.auth.infrastructure.email_crypto import EmailCrypto
from core.post.application.create_post import CreatePost
from core.post.application.delete_post import DeletePost
from core.post.application.get_posts_by_user import GetPostsByUser
from core.post.infrastructure.post_supabase_repo import PostSupabaseRepo
from core.shared.infrastructure.supabase_client import DBClient
from core.user.application.delete_account import DeleteAccount
from core.user.application.get_public_profile import GetPublicProfile
from core.user.application.get_user import GetUser
from core.user.application.get_user_by_name import GetUserByName
from core.user.application.update_user import UpdateUser
from core.user.application.upload_avatar import UploadAvatar
from core.user.infrastructure.avatar_supabase_storage import AvatarSupabaseStorage
from core.user.infrastructure.user_supabase_repo import UserSupabaseRepo


class DependencyContainer:
    def __init__(self) -> None:
        self.db_settings = DBSettings()  # type: ignore[call-arg]
        self.crypto_settings = CryptoSettings()  # type: ignore[call-arg]
        self.db_client = DBClient(self.db_settings)
        self.email_crypto = EmailCrypto(self.crypto_settings)
        self.auth_repository = AuthSupabaseRepo(self.db_client, self.email_crypto)
        self.user_repository = UserSupabaseRepo(self.db_client)
        self.post_repository = PostSupabaseRepo(self.db_client)
        self.avatar_storage = AvatarSupabaseStorage(self.db_client)

    def provision_identity(self) -> ProvisionIdentity:
        return ProvisionIdentity(self.auth_repository)

    def get_user(self) -> GetUser:
        return GetUser(self.user_repository)

    def get_user_by_name(self) -> GetUserByName:
        return GetUserByName(self.user_repository)

    def get_public_profile(self) -> GetPublicProfile:
        return GetPublicProfile(
            self.get_user_by_name(),
            self.get_posts_by_user(),
        )

    def update_user(self) -> UpdateUser:
        return UpdateUser(self.user_repository)

    def upload_avatar(self) -> UploadAvatar:
        return UploadAvatar(self.user_repository, self.avatar_storage)

    def create_post(self) -> CreatePost:
        return CreatePost(self.post_repository)

    def get_posts_by_user(self) -> GetPostsByUser:
        return GetPostsByUser(self.user_repository, self.post_repository)

    def delete_post(self) -> DeletePost:
        return DeletePost(self.post_repository)

    def delete_account(self) -> DeleteAccount:
        return DeleteAccount(
            self.user_repository,
            self.avatar_storage,
            self.auth_repository,
        )


@lru_cache
def get_dependency_container() -> DependencyContainer:
    return DependencyContainer()


def get_ensure_user_provisioned() -> ProvisionIdentity:
    return get_dependency_container().provision_identity()


def get_user_use_case() -> GetUser:
    return get_dependency_container().get_user()


def get_user_by_name_use_case() -> GetUserByName:
    return get_dependency_container().get_user_by_name()


def get_public_profile_use_case() -> GetPublicProfile:
    return get_dependency_container().get_public_profile()


def get_update_user_use_case() -> UpdateUser:
    return get_dependency_container().update_user()


def get_upload_avatar_use_case() -> UploadAvatar:
    return get_dependency_container().upload_avatar()


def get_create_post_use_case() -> CreatePost:
    return get_dependency_container().create_post()


def get_posts_by_user_use_case() -> GetPostsByUser:
    return get_dependency_container().get_posts_by_user()


def get_delete_post_use_case() -> DeletePost:
    return get_dependency_container().delete_post()


def get_delete_account_use_case() -> DeleteAccount:
    return get_dependency_container().delete_account()
