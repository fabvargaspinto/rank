from dataclasses import dataclass
from typing import Protocol

from core.instagram.domain.instagram_connection import InstagramConnection


@dataclass(frozen=True)
class StoredInstagramConnection:
    connection: InstagramConnection
    access_token_encrypted: str

    def __repr__(self) -> str:
        return (
            "StoredInstagramConnection("
            f"connection={self.connection!r}, access_token_encrypted=redacted)"
        )


class InstagramConnectionRepository(Protocol):
    def save(self, stored: StoredInstagramConnection) -> StoredInstagramConnection:
        pass

    def get_by_owner(self, owner_user_id: str) -> StoredInstagramConnection | None:
        pass

    def get_by_account(
        self, instagram_account_id: str
    ) -> StoredInstagramConnection | None:
        pass

    def list_all(self) -> list[StoredInstagramConnection]:
        pass

    def delete_by_owner(self, owner_user_id: str) -> None:
        pass
