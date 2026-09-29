import pytest

from core.post.application.create_post import CreatePost
from core.post.domain.post_error import (
    InvalidPostLinkError,
    InvalidPostTextError,
)
from core.user.domain.user import User
from tests.unit.post.application.fake_post_repo import FakePostRepo

AUTH_ID = "660e8400-e29b-41d4-a716-446655440000"
POST_TEXT = "Me encantó el último tema."
POST_LINK = "https://example.com/track"


class TestCreatePost:
    def setup_method(self):
        self.post_repo = FakePostRepo()
        self.use_case = CreatePost(self.post_repo)
        self.user = User.create_empty()

    def test_creates_post_for_current_user(self):
        post = self.use_case.execute(self.user, POST_TEXT)

        assert post.user_id == self.user.id
        assert post.text.value == POST_TEXT
        assert post.link is None
        assert self.post_repo.posts == [post]

    def test_creates_post_with_link(self):
        post = self.use_case.execute(self.user, POST_TEXT, POST_LINK)

        assert post.link is not None
        assert post.link.value == POST_LINK

    def test_raises_when_text_is_invalid(self):
        with pytest.raises(InvalidPostTextError):
            self.use_case.execute(self.user, "")

    def test_raises_when_link_is_invalid(self):
        with pytest.raises(InvalidPostLinkError):
            self.use_case.execute(self.user, POST_TEXT, "http://example.com")
