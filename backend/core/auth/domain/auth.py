from dataclasses import dataclass

from core.auth.domain.auth_id import AuthId
from core.auth.domain.auth_created_at import AuthCreatedAt
from core.auth.domain.auth_email import AuthEmail
from core.user.domain.user_id import UserId
from core.auth.domain.auth_provider import AuthProvider
from core.auth.domain.auth_oauth_provider import AuthOauthProvider
from core.auth.domain.auth_provider_id import AuthProviderId
from core.auth.domain.auth_password import AuthPassword


@dataclass(frozen=True)
class Auth:
    id: AuthId
    user_id: UserId
    email: AuthEmail
    created_at: AuthCreatedAt
    provider: AuthProvider
    oauth_provider: AuthOauthProvider | None = None
    provider_id: AuthProviderId | None = None
    password: AuthPassword | None = None

    @staticmethod
    def create_email_auth(
        user_id: UserId,
        email: AuthEmail,
        password: AuthPassword,
    ) -> "Auth":
        return Auth(
            id=AuthId.generate(),
            user_id=user_id,
            email=email,
            created_at=AuthCreatedAt.now(),
            provider=AuthProvider.EMAIL,
            oauth_provider=None,
            provider_id=None,
            password=password,
        )

    @staticmethod
    def create_oauth_auth(
        user_id: UserId,
        email: AuthEmail,
        oauth_provider: AuthOauthProvider,
        provider_id: AuthProviderId,
    ) -> "Auth":
        return Auth(
            id=AuthId.generate(),
            user_id=user_id,
            email=email,
            created_at=AuthCreatedAt.now(),
            provider=AuthProvider.OAUTH,
            oauth_provider=oauth_provider,
            provider_id=provider_id,
            password=None,
        )
