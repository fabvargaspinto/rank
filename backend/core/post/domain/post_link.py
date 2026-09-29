from dataclasses import dataclass

from core.post.domain.post_error import InvalidPostLinkError
from core.shared.domain.https_url import HttpsUrl, is_https_url


@dataclass(frozen=True)
class PostLink(HttpsUrl):
    MAX_LENGTH = 2048

    def validate(self, value: str) -> None:
        if len(value) > self.MAX_LENGTH:
            raise InvalidPostLinkError(
                f"La URL debe tener menos de {self.MAX_LENGTH} caracteres"
            )
        if not is_https_url(value):
            raise InvalidPostLinkError("La URL debe ser una URL válida")
