from dataclasses import dataclass

from core.shared.domain.user_id import UserId
from core.user.domain.user_avatar import UserAvatar
from core.user.domain.user_created_at import UserCreatedAt
from core.user.domain.user_description import UserDescription
from core.user.domain.user_display_name import UserDisplayName
from core.user.domain.user_error import (
    InvalidUserLinksReorderError,
    TooManyUserLinksError,
    UserLinkNotFoundError,
)
from core.user.domain.user_link import UserLink
from core.user.domain.user_link_id import UserLinkId
from core.user.domain.user_link_sort_index import UserLinkSortIndex
from core.user.domain.user_link_type import UserLinkType
from core.user.domain.user_link_url import UserLinkUrl
from core.user.domain.user_name import UserName
from core.user.domain.user_updated_at import UserUpdatedAt


@dataclass
class User:
    id: UserId
    name: UserName | None
    display_name: UserDisplayName | None
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
            display_name=None,
            avatar=None,
            description=None,
            links=[],
            created_at=UserCreatedAt.now(),
            updated_at=UserUpdatedAt.now(),
        )

    def has_name(self) -> bool:
        return self.name is not None and self.name.value != ""

    def rename(self, name: str) -> None:
        self.name = UserName(name)
        self._touch()

    def change_display_name(self, display_name: str) -> None:
        self.display_name = UserDisplayName(display_name)
        self._touch()

    def clear_display_name(self) -> None:
        self.display_name = None
        self._touch()

    def describe(self, description: str | None) -> None:
        if description is None or not description.strip():
            self.description = None
        else:
            self.description = UserDescription(description)
        self._touch()

    def change_avatar(self, avatar: str) -> None:
        self.avatar = UserAvatar(avatar)
        self._touch()

    def remove_avatar(self) -> None:
        self.avatar = None
        self._touch()

    def add_link(self, url: str) -> UserLink:
        if len(self.links) >= self.MAX_LINKS:
            raise TooManyUserLinksError(
                f"No se pueden agregar más de {self.MAX_LINKS} links"
            )

        link = UserLink.create_from_url(
            user_id=self.id.value,
            url=url,
            sort_index=len(self.links),
        )
        self.links.append(link)
        self._touch()
        return link

    def replace_links(self, urls: list[str]) -> None:
        if len(urls) > self.MAX_LINKS:
            raise TooManyUserLinksError(
                f"No se pueden agregar más de {self.MAX_LINKS} links"
            )

        remaining = list(self.links)
        replaced: list[UserLink] = []
        for index, url in enumerate(urls):
            link_url = UserLinkUrl(url)
            match_at = next(
                (
                    position
                    for position, link in enumerate(remaining)
                    if link.url == link_url
                ),
                None,
            )
            if match_at is None:
                replaced.append(
                    UserLink.create_from_url(
                        user_id=self.id.value,
                        url=url,
                        sort_index=index,
                    )
                )
                continue

            existing = remaining.pop(match_at)
            replaced.append(
                UserLink(
                    id=existing.id,
                    user_id=existing.user_id,
                    type=UserLinkType.from_host(link_url.host()),
                    url=link_url,
                    sort_index=UserLinkSortIndex(index),
                )
            )

        self.links = replaced
        self._touch()

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
        self._touch()

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
        self._touch()

    def _touch(self) -> None:
        self.updated_at = UserUpdatedAt.now()
