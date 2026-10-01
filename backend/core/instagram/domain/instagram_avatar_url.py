from dataclasses import dataclass

from core.instagram.domain.errors import InvalidInstagramAvatarUrlError


@dataclass(frozen=True)
class InstagramAvatarUrl:
    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str):
            raise InvalidInstagramAvatarUrlError(
                "La URL del avatar de Instagram no es válida"
            )

        normalized = self.value.strip()
        if (
            not normalized.startswith("https://")
            or len(normalized) > 2048
            or any(ch.isspace() for ch in normalized)
        ):
            raise InvalidInstagramAvatarUrlError(
                "La URL del avatar de Instagram no es válida"
            )

        object.__setattr__(self, "value", normalized)
