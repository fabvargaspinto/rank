from core.post.application.application_error import PostNotFoundError
from core.post.domain.post_id import PostId
from core.post.domain.post_repo import PostRepository
from core.user.domain.user import User


class DeletePost:
    def __init__(self, post_repo: PostRepository):
        self.post_repo = post_repo

    def execute(self, user: User, post_id: str) -> None:
        PostId(post_id)
        post = self.post_repo.get_post(post_id)
        if post is None or post.user_id != user.id:
            raise PostNotFoundError("La publicación no existe")

        self.post_repo.delete_post(post_id)
