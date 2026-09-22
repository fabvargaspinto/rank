import pytest

from core.user.domain.user import User
from core.user.domain.user_avatar import UserAvatar
from core.user.domain.user_description import UserDescription
from core.user.domain.user_error import (
    InvalidUserLinksReorderError,
    TooManyUserLinksError,
    UserLinkNotFoundError,
)
from core.user.domain.user_link_type import UserLinkType
from core.user.domain.user_name import UserName

USER_ID = "550e8400-e29b-41d4-a716-446655440000"
YOUTUBE_URL = "https://www.youtube.com/@luna"
INSTAGRAM_URL = "https://www.instagram.com/luna"
DEFAULT_URL = "https://example.com/luna"


def create_user_with_values():
    empty_user = User.create_empty()

    return User(
        id=empty_user.id,
        name=UserName("John Doe"),
        avatar=UserAvatar("https://example.com/avatar.jpg"),
        description=UserDescription("My description"),
        links=[],
        created_at=empty_user.created_at,
        updated_at=empty_user.updated_at,
    )


class TestUser:

    def test_should_create_empty_user(self):
        user = User.create_empty()

        assert user.id is not None
        assert user.name is None
        assert user.avatar is None
        assert user.description is None
        assert user.links == []
        assert user.created_at is not None
        assert user.updated_at is not None

    def test_should_create_user_with_values(self):
        user = create_user_with_values()

        assert user.name.value == "John Doe"
        assert user.avatar.value == "https://example.com/avatar.jpg"
        assert user.description.value == "My description"
        assert user.links == []

    def test_has_name_is_false_for_empty_user(self):
        user = User.create_empty()

        assert user.has_name() is False

    def test_has_name_is_true_when_name_is_set(self):
        user = create_user_with_values()

        assert user.has_name() is True

    def test_update_profile_sets_name_and_optional_fields(self):
        user = User.create_empty()
        previous_updated_at = user.updated_at

        user.update_profile(
            name="luna",
            avatar="https://example.com/avatar.jpg",
            description="Cantautora",
        )

        assert user.name is not None
        assert user.name.value == "luna"
        assert user.avatar is not None
        assert user.avatar.value == "https://example.com/avatar.jpg"
        assert user.description is not None
        assert user.description.value == "Cantautora"
        assert user.updated_at != previous_updated_at

    def test_update_profile_keeps_avatar_when_omitted(self):
        user = create_user_with_values()

        user.update_profile(name="luna", description="Cantautora")

        assert user.avatar is not None
        assert user.avatar.value == "https://example.com/avatar.jpg"
        assert user.description is not None
        assert user.description.value == "Cantautora"

    def test_update_profile_clears_optional_fields(self):
        user = create_user_with_values()

        user.update_profile(name="luna", avatar="", description="   ")

        assert user.name is not None
        assert user.name.value == "luna"
        assert user.avatar is None
        assert user.description is None

    def test_add_link_appends_with_sort_index(self):
        user = User.create_empty()
        previous_updated_at = user.updated_at

        link = user.add_link(url=YOUTUBE_URL)

        assert len(user.links) == 1
        assert link.user_id == user.id
        assert link.type == UserLinkType.YOUTUBE
        assert link.url.value == YOUTUBE_URL
        assert link.sort_index.value == 0
        assert user.updated_at != previous_updated_at

    def test_add_link_assigns_incremental_sort_index(self):
        user = User.create_empty()

        user.add_link(url=YOUTUBE_URL)
        second = user.add_link(url=INSTAGRAM_URL)

        assert second.sort_index.value == 1
        assert [link.sort_index.value for link in user.links] == [0, 1]

    def test_add_link_rejects_when_max_reached(self):
        user = User.create_empty()
        for index in range(User.MAX_LINKS):
            user.add_link(url=f"{DEFAULT_URL}/{index}")

        with pytest.raises(TooManyUserLinksError):
            user.add_link(url=DEFAULT_URL)

    def test_replace_links_infers_types_from_urls(self):
        user = User.create_empty()

        user.replace_links([YOUTUBE_URL, DEFAULT_URL])

        assert [link.type for link in user.links] == [
            UserLinkType.YOUTUBE,
            UserLinkType.DEFAULT,
        ]
        assert [link.sort_index.value for link in user.links] == [0, 1]

    def test_remove_link_reindexes_remaining(self):
        user = User.create_empty()
        first = user.add_link(url=YOUTUBE_URL)
        user.add_link(url=INSTAGRAM_URL)
        third = user.add_link(url=DEFAULT_URL)

        user.remove_link(first.id.value)

        assert [link.url.value for link in user.links] == [INSTAGRAM_URL, DEFAULT_URL]
        assert [link.sort_index.value for link in user.links] == [0, 1]
        assert user.links[1].id == third.id

    def test_remove_link_rejects_unknown_id(self):
        user = User.create_empty()
        user.add_link(url=YOUTUBE_URL)

        with pytest.raises(UserLinkNotFoundError):
            user.remove_link("550e8400-e29b-41d4-a716-446655440099")

    def test_reorder_links_updates_sort_index(self):
        user = User.create_empty()
        first = user.add_link(url=YOUTUBE_URL)
        second = user.add_link(url=INSTAGRAM_URL)
        third = user.add_link(url=DEFAULT_URL)

        user.reorder_links([third.id.value, first.id.value, second.id.value])

        assert [link.id for link in user.links] == [third.id, first.id, second.id]
        assert [link.sort_index.value for link in user.links] == [0, 1, 2]

    def test_reorder_links_rejects_incomplete_list(self):
        user = User.create_empty()
        first = user.add_link(url=YOUTUBE_URL)
        user.add_link(url=INSTAGRAM_URL)

        with pytest.raises(InvalidUserLinksReorderError):
            user.reorder_links([first.id.value])
