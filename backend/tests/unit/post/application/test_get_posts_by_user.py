from datetime import UTC, datetime, timedelta

import pytest

from core.post.application.get_posts_by_user import (
    DEFAULT_LIMIT,
    MAX_LIMIT,
    GetPostsByUser,
)
from core.post.domain.post import Post
from core.post.domain.post_created_at import PostCreatedAt
from core.post.domain.post_id import PostId
from core.post.domain.post_text import PostText
from core.shared.domain.domain_error import InvalidUUIDError
from core.shared.domain.user_id import UserId
from core.user.application.application_error import UserNotFoundError
from core.user.domain.user import User
from tests.unit.post.application.fake_post_repo import FakePostRepo
from tests.unit.user.application.fake_user_repo import FakeUserRepo

USER_ID = "550e8400-e29b-41d4-a716-446655440000"
OTHER_USER_ID = "770e8400-e29b-41d4-a716-446655440000"
BASE_TIME = datetime(2026, 9, 22, 12, 0, 0, tzinfo=UTC)


def _post(
    user_id: str,
    text: str,
    *,
    minutes_ago: int = 0,
) -> Post:
    return Post(
        id=PostId.generate(),
        user_id=UserId(user_id),
        text=PostText(text),
        link=None,
        created_at=PostCreatedAt(BASE_TIME - timedelta(minutes=minutes_ago)),
    )


class TestGetPostsByUser:
    def setup_method(self):
        self.user_repo = FakeUserRepo()
        self.post_repo = FakePostRepo()
        self.use_case = GetPostsByUser(self.user_repo, self.post_repo)
        self.user = User.create_empty()
        self.user_repo.users_by_id[self.user.id.value] = self.user

    def test_returns_posts_for_user_newest_first(self):
        older = _post(self.user.id.value, "Viejo", minutes_ago=10)
        newer = _post(self.user.id.value, "Nuevo", minutes_ago=0)
        self.post_repo.create_post(older)
        self.post_repo.create_post(newer)

        page = self.use_case.execute(self.user.id.value)

        assert [post.text.value for post in page.items] == ["Nuevo", "Viejo"]

    def test_does_not_return_other_users_posts(self):
        own = _post(self.user.id.value, "Mio")
        other = _post(OTHER_USER_ID, "Ajeno")
        self.post_repo.create_post(own)
        self.post_repo.create_post(other)

        page = self.use_case.execute(self.user.id.value)

        assert len(page.items) == 1
        assert page.items[0].text.value == "Mio"

    def test_paginates_posts(self):
        first = _post(self.user.id.value, "Primero", minutes_ago=0)
        second = _post(self.user.id.value, "Segundo", minutes_ago=5)
        self.post_repo.create_post(first)
        self.post_repo.create_post(second)

        page = self.use_case.execute(self.user.id.value, limit=1)
        assert page.next_cursor is not None

        next_page = self.use_case.execute(
            self.user.id.value,
            limit=1,
            cursor=page.next_cursor,
        )

        assert len(next_page.items) == 1
        assert next_page.items[0].text.value == "Segundo"
        assert next_page.next_cursor is None

    def test_uses_default_limit(self):
        for index in range(DEFAULT_LIMIT + 5):
            self.post_repo.create_post(
                _post(
                    self.user.id.value,
                    f"Publicación {index}",
                    minutes_ago=index,
                )
            )

        page = self.use_case.execute(self.user.id.value)

        assert len(page.items) == DEFAULT_LIMIT
        assert page.next_cursor is not None

    def test_caps_limit_at_max(self):
        for index in range(MAX_LIMIT + 5):
            self.post_repo.create_post(
                _post(
                    self.user.id.value,
                    f"Publicación {index}",
                    minutes_ago=index,
                )
            )

        page = self.use_case.execute(
            self.user.id.value,
            limit=MAX_LIMIT + 100,
        )

        assert len(page.items) == MAX_LIMIT

    def test_raises_when_user_is_missing(self):
        with pytest.raises(UserNotFoundError, match="El usuario no existe"):
            self.use_case.execute(USER_ID)

    def test_rejects_an_id_that_is_not_a_uuid(self):
        with pytest.raises(InvalidUUIDError):
            self.use_case.execute("not-a-uuid")
