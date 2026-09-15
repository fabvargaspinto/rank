from datetime import datetime, timedelta, timezone

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import ec
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from jwt import PyJWKClientError

from api.dependencies.auth import (
    AuthJwtSettings,
    CurrentUser,
    get_auth_jwt_settings,
    get_current_user,
    get_jwks_client,
)
from controller.error_handlers import register_error_handlers

ISSUER = "https://example.supabase.co/auth/v1"
AUDIENCE = "authenticated"
AUTH_ID = "660e8400-e29b-41d4-a716-446655440000"
EMAIL = "user@example.com"


class FakeJwksClient:
    def __init__(self, public_key):
        self._public_key = public_key

    def get_signing_key_from_jwt(self, token: str):
        return type("SigningKey", (), {"key": self._public_key})()


def _private_key():
    return ec.generate_private_key(ec.SECP256R1())


def _token(private_key, omit=(), **claims) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": AUTH_ID,
        "email": EMAIL,
        "aud": AUDIENCE,
        "iss": ISSUER,
        "exp": now + timedelta(hours=1),
        "iat": now,
        "role": "authenticated",
        **claims,
    }
    for key in omit:
        payload.pop(key, None)

    return jwt.encode(
        payload,
        private_key,
        algorithm="ES256",
        headers={"kid": "test-key"},
    )


@pytest.fixture
def private_key():
    return _private_key()


@pytest.fixture
def client(private_key):
    app = FastAPI()
    register_error_handlers(app)

    @app.get("/me")
    def me(user: CurrentUser = Depends(get_current_user)):
        return {"auth_id": user.auth_id, "email": user.email}

    app.dependency_overrides[get_auth_jwt_settings] = lambda: AuthJwtSettings(
        jwks_url=f"{ISSUER}/.well-known/jwks.json",
        issuer=ISSUER,
        audience=AUDIENCE,
    )
    app.dependency_overrides[get_jwks_client] = lambda: FakeJwksClient(
        private_key.public_key()
    )

    return TestClient(app)


def _unauthorized(client, **kwargs):
    return client.get("/me", **kwargs)


def _assert_unauthorized(response):
    assert response.status_code == 401
    assert response.json() == {"detail": "El token de autenticación no es válido"}


class TestGetCurrentUser:
    def test_valid_token_creates_current_user(self, client, private_key):
        token = _token(
            private_key,
            sub="custom-auth-id",
            email="other@example.com",
        )

        response = client.get("/me", headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 200
        assert response.json() == {
            "auth_id": "custom-auth-id",
            "email": "other@example.com",
        }

    def test_missing_authorization_returns_401(self, client):
        _assert_unauthorized(_unauthorized(client))

    def test_empty_bearer_returns_401(self, client):
        _assert_unauthorized(
            _unauthorized(client, headers={"Authorization": "Bearer "})
        )

    def test_invalid_token_returns_401(self, client):
        _assert_unauthorized(
            _unauthorized(
                client,
                headers={"Authorization": "Bearer not-a-jwt"},
            )
        )

    def test_non_bearer_scheme_returns_401(self, client, private_key):
        token = _token(private_key)

        _assert_unauthorized(
            _unauthorized(client, headers={"Authorization": f"Basic {token}"})
        )

    def test_expired_token_returns_401(self, client, private_key):
        token = _token(
            private_key,
            exp=datetime.now(timezone.utc) - timedelta(minutes=2),
        )

        _assert_unauthorized(
            _unauthorized(client, headers={"Authorization": f"Bearer {token}"})
        )

    def test_token_signed_with_another_key_returns_401(self, client):
        other_key = _private_key()
        token = _token(other_key)

        _assert_unauthorized(
            _unauthorized(client, headers={"Authorization": f"Bearer {token}"})
        )

    def test_token_without_sub_returns_401(self, client, private_key):
        token = _token(private_key, omit=("sub",))

        _assert_unauthorized(
            _unauthorized(client, headers={"Authorization": f"Bearer {token}"})
        )

    def test_empty_sub_returns_401(self, client, private_key):
        token = _token(private_key, sub="")

        _assert_unauthorized(
            _unauthorized(client, headers={"Authorization": f"Bearer {token}"})
        )

    def test_token_without_email_returns_401(self, client, private_key):
        token = _token(private_key, omit=("email",))

        _assert_unauthorized(
            _unauthorized(client, headers={"Authorization": f"Bearer {token}"})
        )

    def test_wrong_issuer_returns_401(self, client, private_key):
        token = _token(private_key, iss="https://other.example/auth/v1")

        _assert_unauthorized(
            _unauthorized(client, headers={"Authorization": f"Bearer {token}"})
        )

    def test_wrong_audience_returns_401(self, client, private_key):
        token = _token(private_key, aud="anon")

        _assert_unauthorized(
            _unauthorized(client, headers={"Authorization": f"Bearer {token}"})
        )

    def test_jwks_lookup_failure_returns_401(self, client, private_key):
        class _FailingJwks:
            def get_signing_key_from_jwt(self, token: str):
                raise PyJWKClientError("unable to find a signing key")

        client.app.dependency_overrides[get_jwks_client] = lambda: _FailingJwks()
        token = _token(private_key)

        _assert_unauthorized(
            _unauthorized(client, headers={"Authorization": f"Bearer {token}"})
        )
