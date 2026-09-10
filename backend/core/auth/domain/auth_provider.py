from enum import Enum

from core.auth.domain.auth_error import InvalidAuthProviderError


class AuthProvider(Enum):
    GOOGLE = "GOOGLE"
    EMAIL = "EMAIL"

    def __post_init__(self):
        self.validate()

    def validate(self) -> None:
        if self not in [AuthProvider.GOOGLE, AuthProvider.EMAIL]:
            raise InvalidAuthProviderError(f"El proveedor de autenticación debe ser uno de los siguientes: {', '.join([provider.value for provider in AuthProvider])}")

    @classmethod
    def create_google(self) -> "AuthProvider":
        return AuthProvider.GOOGLE

    @classmethod
    def create_email(self) -> "AuthProvider":
        return AuthProvider.EMAIL

    def is_google(self) -> bool:
        return self is AuthProvider.GOOGLE

    def is_email(self) -> bool:
        return self is AuthProvider.EMAIL

    @classmethod
    def from_string(cls, value: str) -> "AuthProvider":
        normalized = value.strip().upper()
        try:
            return cls(normalized)
        except ValueError:
            allowed = ", ".join(provider.value for provider in cls)
            raise InvalidAuthProviderError(f"El proveedor de autenticación debe ser uno de los siguientes: {allowed}")

            