from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.dependencies.auth import (
    AuthJwtSettings,
    CurrentUser,
    get_auth_jwt_settings,
    get_current_user,
    get_jwks_client,
)
from config.dependency_container import get_ensure_user_provisioned
from controller.auth_route import router
from controller.error_handlers import register_error_handlers
from core.auth.application.ensure_user_provisioned import EnsureUserProvisioned
from core.auth.domain.auth_provider import AuthProvider
from core.auth.domain.auth_repo import AuthIdentity
from tests.unit.auth.application.fake_auth_repo import FakeAuthRepo

AUTH_ID = "660e8400-e29b-41d4-a716-446655440000"
EMAIL = "user@example.com"
ISSUER = "https://example.supabase.co/auth/v1"


class _UnusedJwksClient:
    def get_signing_key_from_jwt(self, token: str):
        raise AssertionError("JWKS should not be used without a Bearer token")


def _client(repo: FakeAuthRepo | None = None) -> TestClient:
    app = FastAPI()
    register_error_handlers(app)
    app.include_router(router)

    fake_repo = repo or FakeAuthRepo()
    app.dependency_overrides[get_ensure_user_provisioned] = (
        lambda: EnsureUserProvisioned(fake_repo)
    )
    app.dependency_overrides[get_auth_jwt_settings] = lambda: AuthJwtSettings(
        jwks_url=f"{ISSUER}/.well-known/jwks.json",
        issuer=ISSUER,
    )
    app.dependency_overrides[get_jwks_client] = lambda: _UnusedJwksClient()
    return TestClient(app)


class TestAuthSession:
    def test_missing_authorization_returns_401(self):
        response = _client().post("/auth/session")

        assert response.status_code == 401
        assert response.json() == {
            "detail": "El token de autenticación no es válido"
        }

    def test_token_in_body_is_not_accepted(self):
        response = _client().post(
            "/auth/session",
            json={"access_token": "whatever"},
        )

        assert response.status_code == 401

    def test_valid_current_user_provisions_session(self):
        repo = FakeAuthRepo()
        repo.identity = AuthIdentity(
            id=AUTH_ID,
            provider=AuthProvider.EMAIL,
            provider_id=None,
            email=EMAIL,
        )
        app_client = _client(repo)
        app_client.app.dependency_overrides[get_current_user] = lambda: CurrentUser(
            auth_id=AUTH_ID,
            email=EMAIL,
        )

        response = app_client.post("/auth/session")

        assert response.status_code == 200
        assert response.json() == {"provisioned": True}
        assert repo.find_by_id(AUTH_ID) is not None

    def test_session_is_idempotent(self):
        repo = FakeAuthRepo()
        repo.identity = AuthIdentity(
            id=AUTH_ID,
            provider=AuthProvider.EMAIL,
            provider_id=None,
            email=EMAIL,
        )
        app_client = _client(repo)
        app_client.app.dependency_overrides[get_current_user] = lambda: CurrentUser(
            auth_id=AUTH_ID,
            email=EMAIL,
        )

        first = app_client.post("/auth/session")
        second = app_client.post("/auth/session")

        assert first.json() == {"provisioned": True}
        assert second.json() == {"provisioned": True}
        assert len(repo.auths) == 1
        assert repo.identity_lookups == [AUTH_ID]
