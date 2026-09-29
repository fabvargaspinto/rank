from dataclasses import dataclass

from core.post.domain.post_error import InvalidPostTextError
from core.shared.domain.string import String


@dataclass(frozen=True)
class PostText(String):
    MIN_LENGTH = 1
    MAX_LENGTH = 280

    def validate(self, value: str) -> None:
        if len(value) < self.MIN_LENGTH or len(value) > self.MAX_LENGTH:
            raise InvalidPostTextError(
                f"La publicación debe tener entre "
                f"{self.MIN_LENGTH} y {self.MAX_LENGTH} caracteres"
            )
