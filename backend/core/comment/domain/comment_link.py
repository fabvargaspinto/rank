from dataclasses import dataclass

from core.comment.domain.comment_error import InvalidCommentLinkError
from core.shared.domain.string import String


@dataclass
class CommentLink(String):
    value: str
    MAX_LENGTH = 2048

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        self.value = self.value.strip()

        if not self.value:
            raise InvalidCommentLinkError("La URL debe ser una URL válida")

        if len(self.value) > self.MAX_LENGTH:
            raise InvalidCommentLinkError(
                f"La URL debe tener menos de {self.MAX_LENGTH} caracteres"
            )

        if not self.value.startswith("https://"):
            raise InvalidCommentLinkError("La URL debe ser una URL válida")
