from datetime import UTC, datetime, timedelta

import pytest

from core.comment.application.get_comments_by_user import (
    DEFAULT_LIMIT,
    MAX_LIMIT,
    GetCommentsByUser,
)
from core.comment.domain.comment import Comment
from core.comment.domain.comment_created_at import CommentCreatedAt
from core.comment.domain.comment_id import CommentId
from core.comment.domain.comment_text import CommentText
from core.user.application.application_error import UserNotFoundError
from core.user.domain.user import User
from core.user.domain.user_id import UserId
from tests.unit.comment.application.fake_comment_repo import FakeCommentRepo
from tests.unit.user.application.fake_user_repo import FakeUserRepo

USER_ID = "550e8400-e29b-41d4-a716-446655440000"
OTHER_USER_ID = "770e8400-e29b-41d4-a716-446655440000"
BASE_TIME = datetime(2026, 9, 22, 12, 0, 0, tzinfo=UTC)


def _comment(
    user_id: str,
    text: str,
    *,
    minutes_ago: int = 0,
) -> Comment:
    return Comment(
        id=CommentId.generate(),
        user_id=UserId(user_id),
        text=CommentText(text),
        link=None,
        created_at=CommentCreatedAt(BASE_TIME - timedelta(minutes=minutes_ago)),
    )


class TestGetCommentsByUser:
    def setup_method(self):
        self.user_repo = FakeUserRepo()
        self.comment_repo = FakeCommentRepo()
        self.use_case = GetCommentsByUser(self.user_repo, self.comment_repo)
        self.user = User.create_empty()
        self.user_repo.users_by_id[self.user.id.value] = self.user

    def test_returns_comments_for_user_newest_first(self):
        older = _comment(self.user.id.value, "Viejo", minutes_ago=10)
        newer = _comment(self.user.id.value, "Nuevo", minutes_ago=0)
        self.comment_repo.create_comment(older)
        self.comment_repo.create_comment(newer)

        comments = self.use_case.execute(self.user.id.value)

        assert [comment.text.value for comment in comments] == ["Nuevo", "Viejo"]

    def test_does_not_return_other_users_comments(self):
        own = _comment(self.user.id.value, "Mio")
        other = _comment(OTHER_USER_ID, "Ajeno")
        self.comment_repo.create_comment(own)
        self.comment_repo.create_comment(other)

        comments = self.use_case.execute(self.user.id.value)

        assert len(comments) == 1
        assert comments[0].text.value == "Mio"

    def test_paginates_comments(self):
        first = _comment(self.user.id.value, "Primero", minutes_ago=0)
        second = _comment(self.user.id.value, "Segundo", minutes_ago=5)
        self.comment_repo.create_comment(first)
        self.comment_repo.create_comment(second)

        page = self.use_case.execute(self.user.id.value, limit=1, offset=1)

        assert len(page) == 1
        assert page[0].text.value == "Segundo"

    def test_uses_default_limit(self):
        for index in range(DEFAULT_LIMIT + 5):
            self.comment_repo.create_comment(
                _comment(
                    self.user.id.value,
                    f"Comentario {index}",
                    minutes_ago=index,
                )
            )

        comments = self.use_case.execute(self.user.id.value)

        assert len(comments) == DEFAULT_LIMIT

    def test_caps_limit_at_max(self):
        for index in range(MAX_LIMIT + 5):
            self.comment_repo.create_comment(
                _comment(
                    self.user.id.value,
                    f"Comentario {index}",
                    minutes_ago=index,
                )
            )

        comments = self.use_case.execute(
            self.user.id.value,
            limit=MAX_LIMIT + 100,
        )

        assert len(comments) == MAX_LIMIT

    def test_raises_when_user_is_missing(self):
        with pytest.raises(UserNotFoundError, match="El usuario no existe"):
            self.use_case.execute(USER_ID)
