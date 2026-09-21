from dataclasses import FrozenInstanceError

import pytest

from core.user.domain.user_error import InvalidUserLinkUrlError
from core.user.domain.user_link import UserLink
from core.user.domain.user_link_type import UserLinkType

USER_ID = "550e8400-e29b-41d4-a716-446655440000"
YOUTUBE_URL = "https://www.youtube.com/@luna"
INSTAGRAM_URL = "https://www.instagram.com/luna"
DEFAULT_URL = "https://example.com/luna"


def create_link(
    link_type: str = "youtube",
    url: str = YOUTUBE_URL,
    sort_index: int = 0,
) -> UserLink:
    return UserLink.create(
        user_id=USER_ID,
        type=link_type,
        url=url,
        sort_index=sort_index,
    )


class TestUserLink:

    def test_should_create_youtube_link(self):
        link = create_link()

        assert link.user_id.value == USER_ID
        assert link.type == UserLinkType.YOUTUBE
        assert link.url.value == YOUTUBE_URL
        assert link.sort_index.value == 0
        assert link.id.value is not None

    def test_should_create_instagram_link(self):
        link = create_link(link_type="instagram", url=INSTAGRAM_URL)

        assert link.type == UserLinkType.INSTAGRAM
        assert link.url.value == INSTAGRAM_URL

    def test_should_create_default_link_with_any_https_url(self):
        link = create_link(link_type="default", url=DEFAULT_URL)

        assert link.type == UserLinkType.DEFAULT
        assert link.url.value == DEFAULT_URL

    def test_should_allow_default_type_with_youtube_url(self):
        link = create_link(link_type="default", url=YOUTUBE_URL)

        assert link.type == UserLinkType.DEFAULT
        assert link.url.value == YOUTUBE_URL

    def test_should_generate_different_ids(self):
        first = create_link()
        second = create_link()

        assert first.id != second.id

    def test_should_reject_youtube_type_with_instagram_url(self):
        with pytest.raises(InvalidUserLinkUrlError):
            create_link(link_type="youtube", url=INSTAGRAM_URL)

    def test_should_reject_instagram_type_with_youtube_url(self):
        with pytest.raises(InvalidUserLinkUrlError):
            create_link(link_type="instagram", url=YOUTUBE_URL)

    def test_should_reject_youtube_type_with_unrelated_url(self):
        with pytest.raises(InvalidUserLinkUrlError):
            create_link(link_type="youtube", url=DEFAULT_URL)

    def test_should_be_immutable(self):
        link = create_link()

        with pytest.raises(FrozenInstanceError):
            link.sort_index = link.sort_index
