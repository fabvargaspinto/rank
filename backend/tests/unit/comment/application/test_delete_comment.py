import pytest

from core.comment.application.application_error import CommentNotFoundError
from core.comment.application.delete_comment import DeleteComment
from core.comment.domain.comment import Comment
from core.shared.domain.domain_error import InvalidUUIDError
from core.user.domain.user import User
from tests.unit.comment.application.fake_comment_repo import FakeCommentRepo

AUTH_ID = "660e8400-e29b-41d4-a716-446655440000"


class TestDeleteComment:
    def setup_method(self):
        self.comments = FakeCommentRepo()
        self.use_case = DeleteComment(self.comments)
        self.user = User.create_empty()
        self.user.rename("luna")

    def test_deletes_own_comment(self):
        comment = Comment.create(self.user.id.value, "Un tema nuevo")
        self.comments.create_comment(comment)

        self.use_case.execute(self.user, comment.id.value)

        assert self.comments.comments == []

    def test_rejects_another_users_comment(self):
        other = User.create_empty()
        comment = Comment.create(other.id.value, "Ajeno")
        self.comments.create_comment(comment)

        with pytest.raises(CommentNotFoundError):
            self.use_case.execute(self.user, comment.id.value)

        assert self.comments.comments == [comment]

    def test_rejects_an_id_that_is_not_a_uuid(self):
        with pytest.raises(InvalidUUIDError):
            self.use_case.execute(self.user, "not-a-uuid")
