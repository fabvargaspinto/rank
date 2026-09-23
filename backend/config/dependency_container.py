from functools import lru_cache

from config.crypto_setings import CryptoSettings
from config.db_settings import DBSettings
from core.auth.application.ensure_user_provisioned import EnsureUserProvisioned
from core.auth.application.provision_oauth_user import ProvisionOAuthUser
from core.auth.application.register_with_email import RegisterWithEmail
from core.auth.infrastructure.auth_supabase_repo import AuthSupabaseRepo
from core.auth.infrastructure.email_crypto import EmailCrypto
from core.comment.application.create_comment import CreateComment
from core.comment.application.get_comments_by_user import GetCommentsByUser
from core.comment.infrastructure.comment_supabase_repo import CommentSupabaseRepo
from core.user.application.get_user import GetUser
from core.user.application.get_user_by_name import GetUserByName
from core.user.application.update_user import UpdateUser
from core.user.application.upload_avatar import UploadAvatar
from core.user.infrastructure.avatar_supabase_storage import AvatarSupabaseStorage
from core.user.infrastructure.user_supabase_repo import UserSupabaseRepo
from db.db_client import DBClient


class DependencyContainer:
    def __init__(self) -> None:
        self.db_settings = DBSettings()  # type: ignore[call-arg]
        self.crypto_settings = CryptoSettings()  # type: ignore[call-arg]
        self.db_client = DBClient(self.db_settings)
        self.email_crypto = EmailCrypto(self.crypto_settings)
        self.auth_repository = AuthSupabaseRepo(self.db_client, self.email_crypto)
        self.user_repository = UserSupabaseRepo(self.db_client)
        self.comment_repository = CommentSupabaseRepo(self.db_client)
        self.avatar_storage = AvatarSupabaseStorage(self.db_client)
        self.register_with_email = RegisterWithEmail(self.auth_repository)
        self.provision_oauth_user = ProvisionOAuthUser(self.auth_repository)

    def ensure_user_provisioned(self) -> EnsureUserProvisioned:
        return EnsureUserProvisioned(
            self.auth_repository,
            self.register_with_email,
            self.provision_oauth_user,
        )

    def get_user(self) -> GetUser:
        return GetUser(self.user_repository)

    def get_user_by_name(self) -> GetUserByName:
        return GetUserByName(self.user_repository)

    def update_user(self) -> UpdateUser:
        return UpdateUser(self.user_repository)

    def upload_avatar(self) -> UploadAvatar:
        return UploadAvatar(self.user_repository, self.avatar_storage)

    def create_comment(self) -> CreateComment:
        return CreateComment(self.user_repository, self.comment_repository)

    def get_comments_by_user(self) -> GetCommentsByUser:
        return GetCommentsByUser(self.user_repository, self.comment_repository)


@lru_cache
def get_dependency_container() -> DependencyContainer:
    return DependencyContainer()


def get_ensure_user_provisioned() -> EnsureUserProvisioned:
    return get_dependency_container().ensure_user_provisioned()


def get_user_use_case() -> GetUser:
    return get_dependency_container().get_user()


def get_user_by_name_use_case() -> GetUserByName:
    return get_dependency_container().get_user_by_name()


def get_update_user_use_case() -> UpdateUser:
    return get_dependency_container().update_user()


def get_upload_avatar_use_case() -> UploadAvatar:
    return get_dependency_container().upload_avatar()


def get_create_comment_use_case() -> CreateComment:
    return get_dependency_container().create_comment()


def get_comments_by_user_use_case() -> GetCommentsByUser:
    return get_dependency_container().get_comments_by_user()
