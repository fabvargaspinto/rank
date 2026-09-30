from dataclasses import dataclass

from core.instagram.domain.instagram_account_id import InstagramAccountId
from core.instagram.domain.instagram_username import InstagramUsername


@dataclass(frozen=True)
class InstagramAccount:
    id: InstagramAccountId
    username: InstagramUsername

    @staticmethod
    def create(instagram_account_id: str, username: str) -> "InstagramAccount":
        return InstagramAccount(
            id=InstagramAccountId(instagram_account_id),
            username=InstagramUsername(username),
        )

    def with_username(self, username: str) -> "InstagramAccount":
        return InstagramAccount(
            id=self.id,
            username=InstagramUsername(username),
        )
