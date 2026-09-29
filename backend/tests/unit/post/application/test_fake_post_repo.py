from core.post.domain.post import Post
from core.post.domain.post_page import PostCursor
from tests.unit.post.application.fake_post_repo import FakePostRepo

USER_ID = "550e8400-e29b-41d4-a716-446655440000"
OTHER_USER_ID = "770e8400-e29b-41d4-a716-446655440000"


class TestFakePostRepo:
    def test_create_and_list_by_user(self):
        repo = FakePostRepo()
        first = Post.create(user_id=USER_ID, text="Primero")
        second = Post.create(user_id=USER_ID, text="Segundo")
        other = Post.create(user_id=OTHER_USER_ID, text="Ajeno")

        repo.create_post(first)
        repo.create_post(second)
        repo.create_post(other)

        posts = repo.get_posts_by_user_id(USER_ID, limit=10)

        assert [post.text.value for post in posts] == ["Segundo", "Primero"]

    def test_paginates_results(self):
        repo = FakePostRepo()
        older = Post.create(user_id=USER_ID, text="Viejo")
        newer = Post.create(user_id=USER_ID, text="Nuevo")
        repo.create_post(older)
        repo.create_post(newer)

        first = repo.get_posts_by_user_id(USER_ID, limit=1)
        page = repo.get_posts_by_user_id(
            USER_ID,
            limit=1,
            cursor=PostCursor.from_post(first[0]),
        )

        assert len(page) == 1
        assert page[0].text.value == "Viejo"
