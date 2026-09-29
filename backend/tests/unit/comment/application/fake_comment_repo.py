from core.comment.domain.comment import Comment
from core.comment.domain.comment_page import CommentCursor
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
        cursor: CommentCursor | None = None,
    ) -> list[Comment]:
        if limit <= 0:
            return []

        matching = [
            comment
            for comment in self.comments
            if comment.user_id.value == user_id
        ]
        matching.sort(
            key=lambda comment: (
                comment.created_at.to_isoformat(),
                comment.id.value,
            ),
            reverse=True,
        )
        if cursor is not None:
            position = (cursor.created_at, cursor.id)
            matching = [
                comment
                for comment in matching
                if (comment.created_at.to_isoformat(), comment.id.value) < position
            ]
        return matching[:limit]

    def get_comment(self, comment_id: str) -> Comment | None:
        for comment in self.comments:
            if comment.id.value == comment_id:
                return comment
        return None

    def delete_comment(self, comment_id: str) -> None:
        self.comments = [
            comment for comment in self.comments if comment.id.value != comment_id
        ]
