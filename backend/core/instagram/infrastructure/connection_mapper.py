from core.instagram.domain.connection_created_at import ConnectionCreatedAt
from core.instagram.domain.connection_id import ConnectionId
from core.instagram.domain.connection_updated_at import ConnectionUpdatedAt
from core.instagram.domain.instagram_account import InstagramAccount
from core.instagram.domain.instagram_connection import InstagramConnection
from core.instagram.domain.instagram_connection_repo import StoredInstagramConnection
from core.instagram.domain.owner_user_id import OwnerUserId
from core.instagram.domain.token_expires_at import TokenExpiresAt


class ConnectionMapper:
    def to_stored(self, row: dict[str, object]) -> StoredInstagramConnection:
        avatar = row.get("instagram_avatar_url")
        connection = InstagramConnection(
            id=ConnectionId(str(row["id"])),
            owner_user_id=OwnerUserId(str(row["owner_user_id"])),
            account=InstagramAccount.create(
                str(row["instagram_account_id"]),
                str(row["instagram_username"]),
                str(avatar) if isinstance(avatar, str) else None,
            ),
            token_expires_at=TokenExpiresAt.from_isoformat(str(row["token_expires_at"])),
            created_at=ConnectionCreatedAt.from_isoformat(str(row["created_at"])),
            updated_at=ConnectionUpdatedAt.from_isoformat(str(row["updated_at"])),
        )
        return StoredInstagramConnection(
            connection=connection,
            access_token_encrypted=str(row["access_token_encrypted"]),
        )

    def to_row(self, stored: StoredInstagramConnection) -> tuple[object, ...]:
        connection = stored.connection
        avatar = (
            connection.account.avatar_url.value
            if connection.account.avatar_url is not None
            else None
        )
        return (
            connection.id.value,
            connection.owner_user_id.value,
            connection.account.id.value,
            connection.account.username.value,
            avatar,
            stored.access_token_encrypted,
            connection.token_expires_at.to_isoformat(),
            connection.created_at.to_isoformat(),
            connection.updated_at.to_isoformat(),
        )
