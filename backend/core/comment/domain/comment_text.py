from dataclasses import dataclass

from core.comment.domain.comment_error import InvalidCommentTextError
from core.shared.domain.string import String


@dataclass(frozen=True)
class CommentText(String):
    MIN_LENGTH = 1
    MAX_LENGTH = 280

    def validate(self, value: str) -> None:
        if len(value) < self.MIN_LENGTH or len(value) > self.MAX_LENGTH:
            raise InvalidCommentTextError(
                f"El comentario debe tener entre "
                f"{self.MIN_LENGTH} y {self.MAX_LENGTH} caracteres"
            )
