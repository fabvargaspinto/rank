from enum import StrEnum

from core.auth.domain.auth_error import InvalidAuthProviderError


class AuthProvider(StrEnum):
    EMAIL = "EMAIL"
    GOOGLE = "GOOGLE"

    def is_email(self) -> bool:
        return self == AuthProvider.EMAIL

    def is_oauth(self) -> bool:
        return self != AuthProvider.EMAIL

    @classmethod
    def from_string(cls, value: str) -> "AuthProvider":
        normalized = value.strip().upper()
        try:
            return cls(normalized)
        except ValueError as exc:
            allowed = ", ".join(provider.value for provider in cls)
            raise InvalidAuthProviderError(
                f"El proveedor de autenticación debe ser uno de los siguientes: {allowed}"
            ) from exc

    @classmethod
    def get_all(cls) -> list[str]:
        return [provider.value for provider in cls]
