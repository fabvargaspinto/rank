import pytest

from core.post.application.application_error import PostNotFoundError
from core.post.application.delete_post import DeletePost
from core.post.domain.post import Post
from core.shared.domain.domain_error import InvalidUUIDError
from core.user.domain.user import User
from tests.unit.post.application.fake_post_repo import FakePostRepo

AUTH_ID = "660e8400-e29b-41d4-a716-446655440000"


class TestDeletePost:
    def setup_method(self):
        self.posts = FakePostRepo()
        self.use_case = DeletePost(self.posts)
        self.user = User.create_empty()
        self.user.rename("luna")

    def test_deletes_own_post(self):
        post = Post.create(self.user.id.value, "Un tema nuevo")
        self.posts.create_post(post)

        self.use_case.execute(self.user, post.id.value)

        assert self.posts.posts == []

    def test_rejects_another_users_post(self):
        other = User.create_empty()
        post = Post.create(other.id.value, "Ajeno")
        self.posts.create_post(post)

        with pytest.raises(PostNotFoundError):
            self.use_case.execute(self.user, post.id.value)

        assert self.posts.posts == [post]

    def test_rejects_an_id_that_is_not_a_uuid(self):
        with pytest.raises(InvalidUUIDError):
            self.use_case.execute(self.user, "not-a-uuid")
