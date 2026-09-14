from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Annotated, Protocol

import jwt
from fastapi import Depends, Header
from jwt import InvalidTokenError, PyJWKClient, PyJWKClientError, PyJWKSetError

from config.db_settings import DBSettings
from core.auth.application.application_error import InvalidAuthCredentialsError

_INVALID_TOKEN = "El token de autenticación no es válido"
_JWT_ALGORITHMS = ("ES256", "RS256")
_JWT_AUDIENCE = "authenticated"


class JwtSigningKey(Protocol):
    @property
    def key(self) -> object: ...


class JwtKeySet(Protocol):
    def get_signing_key_from_jwt(self, token: str) -> JwtSigningKey: ...


@dataclass(frozen=True)
class CurrentUser:
    auth_id: str
    email: str


@dataclass(frozen=True)
class AuthJwtSettings:
    jwks_url: str
    issuer: str
    audience: str = _JWT_AUDIENCE


def get_auth_jwt_settings() -> AuthJwtSettings:
    base_url = DBSettings().supabase_url.rstrip("/")
    return AuthJwtSettings(
        jwks_url=f"{base_url}/auth/v1/.well-known/jwks.json",
        issuer=f"{base_url}/auth/v1",
    )


@lru_cache
def _jwks_client(jwks_url: str) -> PyJWKClient:
    return PyJWKClient(jwks_url)


def get_jwks_client(
    jwt_settings: AuthJwtSettings = Depends(get_auth_jwt_settings),
) -> JwtKeySet:
    return _jwks_client(jwt_settings.jwks_url)


def extract_bearer_token(authorization: str | None) -> str:
    if not authorization:
        raise InvalidAuthCredentialsError(_INVALID_TOKEN)

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token.strip():
        raise InvalidAuthCredentialsError(_INVALID_TOKEN)

    return token.strip()


def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
    jwt_settings: AuthJwtSettings = Depends(get_auth_jwt_settings),
    jwks_client: JwtKeySet = Depends(get_jwks_client),
) -> CurrentUser:
    token = extract_bearer_token(authorization)
    payload = _decode_access_token(token, jwt_settings, jwks_client)
    auth_id = payload.get("sub")
    email = payload.get("email")

    if not isinstance(auth_id, str) or not auth_id:
        raise InvalidAuthCredentialsError(_INVALID_TOKEN)
    if not isinstance(email, str) or not email.strip():
        raise InvalidAuthCredentialsError(_INVALID_TOKEN)

    return CurrentUser(auth_id=auth_id, email=email)


def _decode_access_token(
    token: str,
    jwt_settings: AuthJwtSettings,
    jwks_client: JwtKeySet,
) -> dict:
    try:
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        return jwt.decode(
            token,
            signing_key.key,
            algorithms=list(_JWT_ALGORITHMS),
            audience=jwt_settings.audience,
            issuer=jwt_settings.issuer,
            leeway=30,
            options={"require": ["exp", "sub", "aud"]},
        )
    except (InvalidTokenError, PyJWKClientError, PyJWKSetError) as exc:
        raise InvalidAuthCredentialsError(_INVALID_TOKEN) from exc
