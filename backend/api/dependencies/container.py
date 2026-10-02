from dataclasses import dataclass
from functools import lru_cache

from config.crypto_setings import CryptoSettings
from config.db_settings import DBSettings
from config.instagram_settings import InstagramSettings
from config.turso_settings import TursoSettings
from core.auth.application.provision_identity import ProvisionIdentity
from core.auth.infrastructure.auth_supabase_repo import AuthSupabaseRepo
from core.auth.infrastructure.email_crypto import EmailCrypto
from core.instagram.application.capture_instagram_followers import (
    CaptureInstagramFollowers,
)
from core.instagram.application.complete_instagram_oauth import CompleteInstagramOAuth
from core.instagram.application.delete_instagram_user_data import (
    DeleteInstagramUserData,
)
from core.instagram.application.disconnect_instagram import DisconnectInstagram
from core.instagram.application.get_follower_history import GetFollowerHistory
from core.instagram.application.get_instagram_connection import GetInstagramConnection
from core.instagram.application.start_instagram_connection import (
    StartInstagramConnection,
)
from core.instagram.infrastructure.db import create_instagram_db
from core.instagram.infrastructure.follower_snapshot_sql_repo import (
    FollowerSnapshotSqlRepo,
)
from core.instagram.infrastructure.instagram_connection_sql_repo import (
    InstagramConnectionSqlRepo,
)
from core.instagram.infrastructure.meta_instagram_client import MetaInstagramClient
from core.instagram.infrastructure.oauth_state_codec import SignedOAuthStateCodec
from core.instagram.infrastructure.token_crypto import TokenCrypto
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


@dataclass
class InstagramWiring:
    settings: InstagramSettings
    graph: MetaInstagramClient
    codec: SignedOAuthStateCodec
    cipher: TokenCrypto
    connections: InstagramConnectionSqlRepo
    snapshots: FollowerSnapshotSqlRepo


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
        self._instagram: InstagramWiring | None = None

    def _instagram_wiring(self) -> InstagramWiring:
        if self._instagram is None:
            settings = InstagramSettings()  # type: ignore[call-arg]
            db = create_instagram_db(TursoSettings())
            self._instagram = InstagramWiring(
                settings=settings,
                graph=MetaInstagramClient(settings),
                codec=SignedOAuthStateCodec(settings),
                cipher=TokenCrypto(settings),
                connections=InstagramConnectionSqlRepo(db),
                snapshots=FollowerSnapshotSqlRepo(db),
            )
        return self._instagram

    def start_instagram_connection(self) -> StartInstagramConnection:
        wiring = self._instagram_wiring()
        return StartInstagramConnection(wiring.graph, wiring.codec)

    def complete_instagram_oauth(self) -> CompleteInstagramOAuth:
        wiring = self._instagram_wiring()
        return CompleteInstagramOAuth(
            wiring.graph,
            wiring.connections,
            wiring.cipher,
            wiring.codec,
            self.capture_instagram_followers(),
        )

    def disconnect_instagram(self) -> DisconnectInstagram:
        wiring = self._instagram_wiring()
        return DisconnectInstagram(wiring.connections, wiring.snapshots)

    def delete_instagram_user_data(self) -> DeleteInstagramUserData:
        wiring = self._instagram_wiring()
        return DeleteInstagramUserData(wiring.connections, wiring.snapshots)

    def get_instagram_connection(self) -> GetInstagramConnection:
        wiring = self._instagram_wiring()
        return GetInstagramConnection(wiring.connections, wiring.snapshots)

    def get_follower_history(self) -> GetFollowerHistory:
        wiring = self._instagram_wiring()
        return GetFollowerHistory(wiring.connections, wiring.snapshots)

    def capture_instagram_followers(self) -> CaptureInstagramFollowers:
        wiring = self._instagram_wiring()
        return CaptureInstagramFollowers(
            wiring.graph,
            wiring.connections,
            wiring.snapshots,
            wiring.cipher,
        )

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


def get_start_instagram_connection_use_case() -> StartInstagramConnection:
    return get_dependency_container().start_instagram_connection()


def get_complete_instagram_oauth_use_case() -> CompleteInstagramOAuth:
    return get_dependency_container().complete_instagram_oauth()


def get_disconnect_instagram_use_case() -> DisconnectInstagram:
    return get_dependency_container().disconnect_instagram()


def get_delete_instagram_user_data_use_case() -> DeleteInstagramUserData:
    return get_dependency_container().delete_instagram_user_data()


def get_instagram_connection_use_case() -> GetInstagramConnection:
    return get_dependency_container().get_instagram_connection()


def get_follower_history_use_case() -> GetFollowerHistory:
    return get_dependency_container().get_follower_history()


def get_capture_instagram_followers_use_case() -> CaptureInstagramFollowers:
    return get_dependency_container().capture_instagram_followers()
