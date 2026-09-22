from dataclasses import dataclass

from core.comment.domain.comment_error import InvalidCommentTextError
from core.shared.domain.string import String


@dataclass
class CommentText(String):
    value: str
    MIN_LENGTH = 1
    MAX_LENGTH = 280

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        self.value = self.value.strip()

        if len(self.value) < self.MIN_LENGTH or len(self.value) > self.MAX_LENGTH:
            raise InvalidCommentTextError(
                f"El comentario debe tener entre "
                f"{self.MIN_LENGTH} y {self.MAX_LENGTH} caracteres"
            )
