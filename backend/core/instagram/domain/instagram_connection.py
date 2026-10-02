from dataclasses import dataclass
from datetime import datetime

from core.instagram.domain.connection_created_at import ConnectionCreatedAt
from core.instagram.domain.connection_id import ConnectionId
from core.instagram.domain.connection_updated_at import ConnectionUpdatedAt
from core.instagram.domain.instagram_account import InstagramAccount
from core.instagram.domain.owner_user_id import OwnerUserId
from core.instagram.domain.token_expires_at import TokenExpiresAt


@dataclass(frozen=True)
class InstagramConnection:
    id: ConnectionId
    owner_user_id: OwnerUserId
    account: InstagramAccount
    token_expires_at: TokenExpiresAt
    created_at: ConnectionCreatedAt
    updated_at: ConnectionUpdatedAt

    @staticmethod
    def connect(
        owner_user_id: str,
        instagram_account_id: str,
        username: str,
        token_expires_at: datetime,
        avatar_url: str | None = None,
    ) -> "InstagramConnection":
        now = ConnectionCreatedAt.now()
        return InstagramConnection(
            id=ConnectionId.generate(),
            owner_user_id=OwnerUserId(owner_user_id),
            account=InstagramAccount.create(
                instagram_account_id,
                username,
                avatar_url,
            ),
            token_expires_at=TokenExpiresAt(token_expires_at),
            created_at=now,
            updated_at=ConnectionUpdatedAt(now.value),
        )

    def belongs_to(self, owner_user_id: str) -> bool:
        return self.owner_user_id == OwnerUserId(owner_user_id)

    def reauthorize(
        self,
        instagram_account_id: str,
        username: str,
        token_expires_at: datetime,
        avatar_url: str | None = None,
    ) -> "InstagramConnection":
        return InstagramConnection(
            id=self.id,
            owner_user_id=self.owner_user_id,
            account=InstagramAccount.create(
                instagram_account_id,
                username,
                avatar_url,
            ),
            token_expires_at=TokenExpiresAt(token_expires_at),
            created_at=self.created_at,
            updated_at=ConnectionUpdatedAt.now(),
        )

    def with_token_expiry(self, token_expires_at: datetime) -> "InstagramConnection":
        return InstagramConnection(
            id=self.id,
            owner_user_id=self.owner_user_id,
            account=self.account,
            token_expires_at=TokenExpiresAt(token_expires_at),
            created_at=self.created_at,
            updated_at=ConnectionUpdatedAt.now(),
        )

    def with_profile(
        self,
        username: str,
        avatar_url: str | None,
    ) -> "InstagramConnection":
        return InstagramConnection(
            id=self.id,
            owner_user_id=self.owner_user_id,
            account=InstagramAccount.create(
                self.account.id.value,
                username,
                avatar_url,
            ),
            token_expires_at=self.token_expires_at,
            created_at=self.created_at,
            updated_at=ConnectionUpdatedAt.now(),
        )

    def token_is_expired(self, at: datetime) -> bool:
        return at >= self.token_expires_at.value
