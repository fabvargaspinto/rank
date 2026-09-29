from core.post.domain.post import Post
from core.post.domain.post_repo import PostRepository
from core.user.domain.user import User


class CreatePost:
    def __init__(self, post_repo: PostRepository):
        self.post_repo = post_repo

    def execute(
        self,
        user: User,
        text: str,
        link: str | None = None,
    ) -> Post:
        post = Post.create(
            user_id=user.id.value,
            text=text,
            link=link,
        )
        return self.post_repo.create_post(post)
