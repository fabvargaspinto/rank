from dataclasses import dataclass

from core.instagram.domain.instagram_account_id import InstagramAccountId
from core.instagram.domain.instagram_avatar_url import InstagramAvatarUrl
from core.instagram.domain.instagram_username import InstagramUsername


@dataclass(frozen=True)
class InstagramAccount:
    id: InstagramAccountId
    username: InstagramUsername
    avatar_url: InstagramAvatarUrl | None = None

    @staticmethod
    def create(
        instagram_account_id: str,
        username: str,
        avatar_url: str | None = None,
    ) -> "InstagramAccount":
        return InstagramAccount(
            id=InstagramAccountId(instagram_account_id),
            username=InstagramUsername(username),
            avatar_url=(
                InstagramAvatarUrl(avatar_url)
                if isinstance(avatar_url, str) and avatar_url.strip()
                else None
            ),
        )

    def with_username(self, username: str) -> "InstagramAccount":
        return InstagramAccount(
            id=self.id,
            username=InstagramUsername(username),
            avatar_url=self.avatar_url,
        )

    def with_avatar_url(self, avatar_url: str | None) -> "InstagramAccount":
        return InstagramAccount.create(
            self.id.value,
            self.username.value,
            avatar_url,
        )
