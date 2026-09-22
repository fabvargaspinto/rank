from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.dependencies.auth import (
    AuthJwtSettings,
    CurrentUser,
    get_auth_jwt_settings,
    get_current_user,
    get_jwks_client,
)
from config.dependency_container import get_create_comment_use_case
from controller.comment_route import router
from controller.error_handlers import register_error_handlers
from core.comment.application.create_comment import CreateComment
from core.user.domain.user import User
from tests.unit.comment.application.fake_comment_repo import FakeCommentRepo
from tests.unit.user.application.fake_user_repo import FakeUserRepo

AUTH_ID = "660e8400-e29b-41d4-a716-446655440000"
OTHER_AUTH_ID = "770e8400-e29b-41d4-a716-446655440000"
ISSUER = "https://example.supabase.co/auth/v1"


class _UnusedJwksClient:
    def get_signing_key_from_jwt(self, token: str):
        raise AssertionError("JWKS should not be used without a Bearer token")


def _client(
    user_repo: FakeUserRepo | None = None,
    comment_repo: FakeCommentRepo | None = None,
) -> TestClient:
    app = FastAPI()
    register_error_handlers(app)
    app.include_router(router)

    fake_user_repo = user_repo or FakeUserRepo()
    fake_comment_repo = comment_repo or FakeCommentRepo()
    app.dependency_overrides[get_create_comment_use_case] = lambda: CreateComment(
        fake_user_repo,
        fake_comment_repo,
    )
    app.dependency_overrides[get_auth_jwt_settings] = lambda: AuthJwtSettings(
        jwks_url=f"{ISSUER}/.well-known/jwks.json",
        issuer=ISSUER,
    )
    app.dependency_overrides[get_jwks_client] = lambda: _UnusedJwksClient()
    return TestClient(app)


class TestCreateComment:
    def test_missing_authorization_returns_401(self):
        response = _client().post(
            f"/users/{AUTH_ID}/comments",
            json={"text": "Hola"},
        )

        assert response.status_code == 401
        assert response.json() == {
            "detail": "El token de autenticación no es válido"
        }

    def test_other_auth_id_returns_404(self):
        app_client = _client()
        app_client.app.dependency_overrides[get_current_user] = lambda: CurrentUser(
            auth_id=AUTH_ID,
            email="user@example.com",
        )

        response = app_client.post(
            f"/users/{OTHER_AUTH_ID}/comments",
            json={"text": "Hola"},
        )

        assert response.status_code == 404
        assert response.json() == {"detail": "El usuario no existe"}

    def test_creates_comment_for_current_user(self):
        user_repo = FakeUserRepo()
        comment_repo = FakeCommentRepo()
        user = User.create_empty()
        user_repo.users_by_auth_id[AUTH_ID] = user
        app_client = _client(user_repo, comment_repo)
        app_client.app.dependency_overrides[get_current_user] = lambda: CurrentUser(
            auth_id=AUTH_ID,
            email="user@example.com",
        )

        response = app_client.post(
            f"/users/{AUTH_ID}/comments",
            json={
                "text": "Me encantó el último tema.",
                "link": "https://example.com/track",
            },
        )

        assert response.status_code == 201
        body = response.json()
        assert body["user_id"] == user.id.value
        assert body["text"] == "Me encantó el último tema."
        assert body["link"] == "https://example.com/track"
        assert body["id"]
        assert body["created_at"]
        assert len(comment_repo.comments) == 1

    def test_unknown_auth_id_returns_404(self):
        app_client = _client()
        app_client.app.dependency_overrides[get_current_user] = lambda: CurrentUser(
            auth_id=AUTH_ID,
            email="user@example.com",
        )

        response = app_client.post(
            f"/users/{AUTH_ID}/comments",
            json={"text": "Hola"},
        )

        assert response.status_code == 404
        assert response.json() == {"detail": "El usuario no existe"}

    def test_invalid_text_returns_400(self):
        user_repo = FakeUserRepo()
        user_repo.users_by_auth_id[AUTH_ID] = User.create_empty()
        app_client = _client(user_repo)
        app_client.app.dependency_overrides[get_current_user] = lambda: CurrentUser(
            auth_id=AUTH_ID,
            email="user@example.com",
        )

        response = app_client.post(
            f"/users/{AUTH_ID}/comments",
            json={"text": "   "},
        )

        assert response.status_code == 400
