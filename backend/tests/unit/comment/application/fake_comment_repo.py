from core.comment.domain.comment import Comment
from core.comment.domain.comment_repo import CommentRepository


class FakeCommentRepo(CommentRepository):
    def __init__(self) -> None:
        self.comments: list[Comment] = []

    def create_comment(self, comment: Comment) -> Comment:
        self.comments.append(comment)
        return comment

    def get_comments_by_user_id(
        self,
        user_id: str,
        limit: int,
        offset: int,
    ) -> list[Comment]:
        if limit <= 0:
            return []

        start = max(offset, 0)
        matching = [
            comment
            for comment in self.comments
            if comment.user_id.value == user_id
        ]
        matching.sort(key=lambda comment: comment.created_at.value, reverse=True)
        return matching[start : start + limit]
