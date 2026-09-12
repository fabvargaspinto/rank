from dataclasses import dataclass

from core.auth.domain.auth_error import InvalidAuthProviderError
from core.auth.domain.auth_provider import AuthProvider
from core.auth.domain.auth_provider_id import AuthProviderId


@dataclass(frozen=True)
class AuthMethod:
    provider: AuthProvider
    provider_id: AuthProviderId | None = None

    def __post_init__(self) -> None:
        if self.provider.is_email():
            if self.provider_id is not None:
                raise InvalidAuthProviderError(
                    "El método email no debe tener provider_id"
                )
            return

        if self.provider_id is None:
            raise InvalidAuthProviderError("El método OAuth requiere provider_id")

    @staticmethod
    def email() -> "AuthMethod":
        return AuthMethod(provider=AuthProvider.EMAIL, provider_id=None)

    @staticmethod
    def oauth(provider: AuthProvider, provider_id: str) -> "AuthMethod":
        if not provider.is_oauth():
            raise InvalidAuthProviderError("El proveedor debe ser un proveedor OAuth")

        return AuthMethod(
            provider=provider,
            provider_id=AuthProviderId(provider_id),
        )


    @staticmethod
    def from_primitive(primitive: dict) -> "AuthMethod":
        return AuthMethod(
            provider=AuthProvider.from_string(primitive["provider"]),
            provider_id=None if primitive["provider"] == AuthProvider.EMAIL.value else AuthProviderId(primitive["provider_id"]),
        )

    def to_primitive(self) -> dict:
        return {
            "provider": self.provider.value,
            "provider_id": self.provider_id.value if self.provider_id is not None else None,
        }