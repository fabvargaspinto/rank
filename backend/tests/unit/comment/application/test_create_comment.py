import pytest

from core.comment.application.create_comment import CreateComment
from core.comment.domain.comment_error import (
    InvalidCommentLinkError,
    InvalidCommentTextError,
)
from core.user.application.application_error import UserNotFoundError
from core.user.domain.user import User
from tests.unit.comment.application.fake_comment_repo import FakeCommentRepo
from tests.unit.user.application.fake_user_repo import FakeUserRepo

AUTH_ID = "660e8400-e29b-41d4-a716-446655440000"
COMMENT_TEXT = "Me encantó el último tema."
COMMENT_LINK = "https://example.com/track"


class TestCreateComment:
    def setup_method(self):
        self.user_repo = FakeUserRepo()
        self.comment_repo = FakeCommentRepo()
        self.use_case = CreateComment(self.user_repo, self.comment_repo)
        self.user = User.create_empty()
        self.user_repo.users_by_auth_id[AUTH_ID] = self.user

    def test_creates_comment_for_current_user(self):
        comment = self.use_case.execute(AUTH_ID, COMMENT_TEXT)

        assert comment.user_id == self.user.id
        assert comment.text.value == COMMENT_TEXT
        assert comment.link is None
        assert self.comment_repo.comments == [comment]

    def test_creates_comment_with_link(self):
        comment = self.use_case.execute(AUTH_ID, COMMENT_TEXT, COMMENT_LINK)

        assert comment.link is not None
        assert comment.link.value == COMMENT_LINK

    def test_raises_when_user_is_missing(self):
        self.user_repo.users_by_auth_id.clear()

        with pytest.raises(UserNotFoundError, match="El usuario no existe"):
            self.use_case.execute(AUTH_ID, COMMENT_TEXT)

    def test_raises_when_text_is_invalid(self):
        with pytest.raises(InvalidCommentTextError):
            self.use_case.execute(AUTH_ID, "")

    def test_raises_when_link_is_invalid(self):
        with pytest.raises(InvalidCommentLinkError):
            self.use_case.execute(AUTH_ID, COMMENT_TEXT, "http://example.com")
