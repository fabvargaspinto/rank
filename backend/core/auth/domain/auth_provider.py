from dataclasses import dataclass
from enum import StrEnum

from core.auth.domain.auth_error import InvalidProviderError


class ProviderKind(StrEnum):
    GOOGLE = "GOOGLE"
    CREDENTIALS = "CREDENTIALS"


@dataclass(frozen=True)
class Provider:
    value: ProviderKind

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", self._validate(self.value))

    @staticmethod
    def _validate(value: str | ProviderKind) -> ProviderKind:
        if isinstance(value, ProviderKind):
            return value
        if not value or not str(value).strip():
            raise InvalidProviderError("Provider is required")
        try:
            return ProviderKind(str(value).strip().upper())
        except ValueError:
            raise InvalidProviderError("Invalid provider") from None

    @classmethod
    def from_str(cls, value: str) -> "Provider":
        return cls(value)

    @classmethod
    def from_google(cls) -> "Provider":
        return cls(ProviderKind.GOOGLE)

    @classmethod
    def from_credentials(cls) -> "Provider":
        return cls(ProviderKind.CREDENTIALS)

    def is_google(self) -> bool:
        return self.value is ProviderKind.GOOGLE

    def is_credentials(self) -> bool:
        return self.value is ProviderKind.CREDENTIALS

    def __str__(self) -> str:
        return self.value
