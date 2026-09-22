from dataclasses import dataclass

from core.user.domain.user_error import InvalidUserLinkUrlError
from core.user.domain.user_id import UserId
from core.user.domain.user_link_id import UserLinkId
from core.user.domain.user_link_sort_index import UserLinkSortIndex
from core.user.domain.user_link_type import UserLinkType
from core.user.domain.user_link_url import UserLinkUrl


@dataclass(frozen=True)
class UserLink:
    id: UserLinkId
    user_id: UserId
    type: UserLinkType
    url: UserLinkUrl
    sort_index: UserLinkSortIndex

    def __post_init__(self) -> None:
        if self.type.is_default():
            return

        if self.url.host() not in self.type.hosts():
            raise InvalidUserLinkUrlError(
                f"La URL no corresponde al tipo {self.type.value}"
            )

    @staticmethod
    def create(
        user_id: str,
        type: str,
        url: str,
        sort_index: int,
    ) -> "UserLink":
        return UserLink(
            id=UserLinkId.generate(),
            user_id=UserId(user_id),
            type=UserLinkType.from_string(type),
            url=UserLinkUrl(url),
            sort_index=UserLinkSortIndex(sort_index),
        )

    @staticmethod
    def create_from_url(
        user_id: str,
        url: str,
        sort_index: int,
    ) -> "UserLink":
        link_url = UserLinkUrl(url)
        return UserLink(
            id=UserLinkId.generate(),
            user_id=UserId(user_id),
            type=UserLinkType.from_host(link_url.host()),
            url=link_url,
            sort_index=UserLinkSortIndex(sort_index),
        )
