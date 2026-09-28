from dataclasses import dataclass
from urllib.parse import urlsplit

from core.shared.domain.domain_error import InvalidHttpsUrlError
from core.shared.domain.string import String


def is_https_url(value: str) -> bool:
    if any(char.isspace() for char in value):
        return False
    parts = urlsplit(value)
    return parts.scheme == "https" and bool(parts.hostname)


@dataclass(frozen=True)
class HttpsUrl(String):
    def validate(self, value: str) -> None:
        if not is_https_url(value):
            raise InvalidHttpsUrlError("La URL debe ser una URL válida")
