from core.comment.domain.comment import Comment
from tests.unit.comment.application.fake_comment_repo import FakeCommentRepo

USER_ID = "550e8400-e29b-41d4-a716-446655440000"
OTHER_USER_ID = "770e8400-e29b-41d4-a716-446655440000"


class TestFakeCommentRepo:
    def test_create_and_list_by_user(self):
        repo = FakeCommentRepo()
        first = Comment.create(user_id=USER_ID, text="Primero")
        second = Comment.create(user_id=USER_ID, text="Segundo")
        other = Comment.create(user_id=OTHER_USER_ID, text="Ajeno")

        repo.create_comment(first)
        repo.create_comment(second)
        repo.create_comment(other)

        comments = repo.get_comments_by_user_id(USER_ID, limit=10, offset=0)

        assert [comment.text.value for comment in comments] == ["Segundo", "Primero"]

    def test_paginates_results(self):
        repo = FakeCommentRepo()
        older = Comment.create(user_id=USER_ID, text="Viejo")
        newer = Comment.create(user_id=USER_ID, text="Nuevo")
        repo.create_comment(older)
        repo.create_comment(newer)

        page = repo.get_comments_by_user_id(USER_ID, limit=1, offset=1)

        assert len(page) == 1
        assert page[0].text.value == "Viejo"
