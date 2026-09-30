from typing import Protocol

SCHEMA_STATEMENTS = (
    """
    CREATE TABLE IF NOT EXISTS instagram_connections (
        id TEXT PRIMARY KEY,
        owner_user_id TEXT NOT NULL UNIQUE,
        instagram_account_id TEXT NOT NULL UNIQUE,
        instagram_username TEXT NOT NULL,
        access_token_encrypted TEXT NOT NULL,
        token_expires_at TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_instagram_connections_account
        ON instagram_connections (instagram_account_id)
    """,
    """
    CREATE TABLE IF NOT EXISTS follower_snapshots (
        id TEXT PRIMARY KEY,
        instagram_account_id TEXT NOT NULL,
        followers_count INTEGER NOT NULL,
        week_start TEXT NOT NULL,
        captured_at TEXT NOT NULL,
        UNIQUE (instagram_account_id, week_start)
    )
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_follower_snapshots_account_week
        ON follower_snapshots (instagram_account_id, week_start)
    """,
)


class SqlDatabase(Protocol):
    def execute(
        self,
        sql: str,
        params: tuple[object, ...] = (),
    ) -> list[dict[str, object]]:
        pass
