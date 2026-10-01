from __future__ import annotations

import sqlite3
from pathlib import Path
from threading import Lock

from core.instagram.infrastructure.error_infrastructure import InstagramDbError
from core.instagram.infrastructure.sql import SCHEMA_STATEMENTS


def sqlite_path(url: str) -> str:
    if url == ":memory:" or url.startswith("file:mem"):
        return url
    stripped = url.removeprefix("file:").removeprefix("//")
    if stripped.startswith("./"):
        return stripped
    return stripped


class SqliteDatabase:
    def __init__(self, url: str = ":memory:") -> None:
        path = sqlite_path(url)
        if path not in {":memory:"} and not path.startswith("file:") and path:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        self._connection = sqlite3.connect(path, check_same_thread=False)
        self._connection.row_factory = sqlite3.Row
        self._lock = Lock()
        self._migrated = False
        self.ensure_schema()

    def ensure_schema(self) -> None:
        with self._lock:
            if self._migrated:
                return
            try:
                for statement in SCHEMA_STATEMENTS:
                    self._connection.execute(statement)
                columns = self._connection.execute(
                    "PRAGMA table_info(instagram_connections)"
                ).fetchall()
                names = {str(row["name"]) for row in columns}
                if "instagram_avatar_url" not in names:
                    self._connection.execute(
                        "ALTER TABLE instagram_connections "
                        "ADD COLUMN instagram_avatar_url TEXT"
                    )
                self._connection.commit()
            except sqlite3.Error as exc:
                raise InstagramDbError("No se pudo preparar la base de Instagram") from exc
            self._migrated = True

    def execute(
        self,
        sql: str,
        params: tuple[object, ...] = (),
    ) -> list[dict[str, object]]:
        with self._lock:
            try:
                cursor = self._connection.execute(sql, params)
                self._connection.commit()
                rows = cursor.fetchall()
            except sqlite3.Error as exc:
                raise InstagramDbError("No se pudo guardar los datos de Instagram") from exc
        return [dict(row) for row in rows]

    def close(self) -> None:
        self._connection.close()
