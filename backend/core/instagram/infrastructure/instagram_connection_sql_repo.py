from core.instagram.domain.instagram_connection_repo import (
    InstagramConnectionRepository,
    StoredInstagramConnection,
)
from core.instagram.infrastructure.connection_mapper import ConnectionMapper
from core.instagram.infrastructure.sql import SqlDatabase

_SAVE_SQL = """
INSERT INTO instagram_connections (
    id,
    owner_user_id,
    instagram_account_id,
    instagram_username,
    access_token_encrypted,
    token_expires_at,
    created_at,
    updated_at
) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
ON CONFLICT(id) DO UPDATE SET
    owner_user_id = excluded.owner_user_id,
    instagram_account_id = excluded.instagram_account_id,
    instagram_username = excluded.instagram_username,
    access_token_encrypted = excluded.access_token_encrypted,
    token_expires_at = excluded.token_expires_at,
    updated_at = excluded.updated_at
"""


class InstagramConnectionSqlRepo(InstagramConnectionRepository):
    def __init__(self, db: SqlDatabase) -> None:
        self._db = db
        self._mapper = ConnectionMapper()

    def save(self, stored: StoredInstagramConnection) -> StoredInstagramConnection:
        self._db.execute(_SAVE_SQL, self._mapper.to_row(stored))
        return stored

    def get_by_owner(self, owner_user_id: str) -> StoredInstagramConnection | None:
        rows = self._db.execute(
            "SELECT * FROM instagram_connections WHERE owner_user_id = ? LIMIT 1",
            (owner_user_id,),
        )
        return self._one(rows)

    def get_by_account(
        self, instagram_account_id: str
    ) -> StoredInstagramConnection | None:
        rows = self._db.execute(
            "SELECT * FROM instagram_connections WHERE instagram_account_id = ? LIMIT 1",
            (instagram_account_id,),
        )
        return self._one(rows)

    def list_all(self) -> list[StoredInstagramConnection]:
        rows = self._db.execute(
            "SELECT * FROM instagram_connections ORDER BY created_at ASC"
        )
        return [self._mapper.to_stored(row) for row in rows]

    def delete_by_owner(self, owner_user_id: str) -> None:
        self._db.execute(
            "DELETE FROM instagram_connections WHERE owner_user_id = ?",
            (owner_user_id,),
        )

    def _one(self, rows: list[dict[str, object]]) -> StoredInstagramConnection | None:
        if not rows:
            return None
        return self._mapper.to_stored(rows[0])
