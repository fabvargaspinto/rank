from dataclasses import dataclass

from core.user.domain.user_avatar import UserAvatar
from core.user.domain.user_created_at import UserCreatedAt
from core.user.domain.user_description import UserDescription
from core.user.domain.user_error import (
    InvalidUserLinksReorderError,
    TooManyUserLinksError,
    UserLinkNotFoundError,
)
from core.user.domain.user_id import UserId
from core.user.domain.user_link import UserLink
from core.user.domain.user_link_id import UserLinkId
from core.user.domain.user_link_sort_index import UserLinkSortIndex
from core.user.domain.user_name import UserName
from core.user.domain.user_updated_at import UserUpdatedAt


@dataclass
class User:
    id: UserId
    name: UserName | None
    avatar: UserAvatar | None
    description: UserDescription | None
    links: list[UserLink]
    created_at: UserCreatedAt
    updated_at: UserUpdatedAt

    MAX_LINKS = UserLinkSortIndex.MAX + 1

    @staticmethod
    def create_empty() -> "User":
        return User(
            id=UserId.generate(),
            name=None,
            avatar=None,
            description=None,
            links=[],
            created_at=UserCreatedAt.now(),
            updated_at=UserUpdatedAt.now(),
        )

    def has_name(self) -> bool:
        return self.name is not None and self.name.value != ""

    def update_profile(
        self,
        name: str,
        avatar: str | None = None,
        description: str | None = None,
    ) -> None:
        self.name = UserName(name)

        avatar_value = avatar.strip() if avatar else ""
        self.avatar = UserAvatar(avatar_value) if avatar_value else None

        if description is None or not description.strip():
            self.description = None
        else:
            self.description = UserDescription(description)

        self.updated_at = UserUpdatedAt.now()

    def add_link(self, type: str, url: str) -> UserLink:
        if len(self.links) >= self.MAX_LINKS:
            raise TooManyUserLinksError(
                f"No se pueden agregar más de {self.MAX_LINKS} links"
            )

        link = UserLink.create(
            user_id=self.id.value,
            type=type,
            url=url,
            sort_index=len(self.links),
        )
        self.links.append(link)
        self.updated_at = UserUpdatedAt.now()
        return link

    def remove_link(self, link_id: str) -> None:
        target_id = UserLinkId(link_id)
        remaining = [link for link in self.links if link.id != target_id]
        if len(remaining) == len(self.links):
            raise UserLinkNotFoundError("El link no existe")

        self.links = [
            UserLink(
                id=link.id,
                user_id=link.user_id,
                type=link.type,
                url=link.url,
                sort_index=UserLinkSortIndex(index),
            )
            for index, link in enumerate(remaining)
        ]
        self.updated_at = UserUpdatedAt.now()

    def reorder_links(self, link_ids: list[str]) -> None:
        if len(link_ids) != len(self.links):
            raise InvalidUserLinksReorderError(
                "La lista de links a reordenar no coincide"
            )

        links_by_id = {link.id.value: link for link in self.links}
        if set(link_ids) != set(links_by_id):
            raise InvalidUserLinksReorderError(
                "La lista de links a reordenar no coincide"
            )

        self.links = [
            UserLink(
                id=links_by_id[link_id].id,
                user_id=links_by_id[link_id].user_id,
                type=links_by_id[link_id].type,
                url=links_by_id[link_id].url,
                sort_index=UserLinkSortIndex(index),
            )
            for index, link_id in enumerate(link_ids)
        ]
        self.updated_at = UserUpdatedAt.now()
