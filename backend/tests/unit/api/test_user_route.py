from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.dependencies.auth import (
    AuthJwtSettings,
    CurrentUser,
    get_auth_jwt_settings,
    get_current_user,
    get_jwks_client,
)
from config.dependency_container import (
    get_update_user_use_case,
    get_user_by_name_use_case,
    get_user_use_case,
)
from controller.error_handlers import register_error_handlers
from controller.user_route import router
from core.user.application.get_user import GetUser
from core.user.application.get_user_by_name import GetUserByName
from core.user.application.update_user import UpdateUser
from core.user.domain.user import User
from core.user.domain.user_avatar import UserAvatar
from core.user.domain.user_description import UserDescription
from core.user.domain.user_name import UserName
from tests.unit.user.application.fake_user_repo import FakeUserRepo

AUTH_ID = "660e8400-e29b-41d4-a716-446655440000"
OTHER_AUTH_ID = "770e8400-e29b-41d4-a716-446655440000"
ISSUER = "https://example.supabase.co/auth/v1"
USERNAME = "luna"


class _UnusedJwksClient:
    def get_signing_key_from_jwt(self, token: str):
        raise AssertionError("JWKS should not be used without a Bearer token")


def _named_user() -> User:
    user = User.create_empty()
    user.name = UserName("Luna Reyes")
    user.avatar = UserAvatar("https://example.com/avatar.jpg")
    user.description = UserDescription("Cantautora")
    return user


def _client(repo: FakeUserRepo | None = None) -> TestClient:
    app = FastAPI()
    register_error_handlers(app)
    app.include_router(router)

    fake_repo = repo or FakeUserRepo()
    app.dependency_overrides[get_user_use_case] = lambda: GetUser(fake_repo)
    app.dependency_overrides[get_user_by_name_use_case] = (
        lambda: GetUserByName(fake_repo)
    )
    app.dependency_overrides[get_update_user_use_case] = (
        lambda: UpdateUser(fake_repo)
    )
    app.dependency_overrides[get_auth_jwt_settings] = lambda: AuthJwtSettings(
        jwks_url=f"{ISSUER}/.well-known/jwks.json",
        issuer=ISSUER,
    )
    app.dependency_overrides[get_jwks_client] = lambda: _UnusedJwksClient()
    return TestClient(app)


class TestGetUserByAuthId:
    def test_missing_authorization_returns_401(self):
        response = _client().get(f"/users/{AUTH_ID}")

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

        response = app_client.get(f"/users/{OTHER_AUTH_ID}")

        assert response.status_code == 404
        assert response.json() == {"detail": "El usuario no existe"}

    def test_valid_current_user_returns_profile(self):
        repo = FakeUserRepo()
        user = _named_user()
        repo.users_by_auth_id[AUTH_ID] = user
        app_client = _client(repo)
        app_client.app.dependency_overrides[get_current_user] = lambda: CurrentUser(
            auth_id=AUTH_ID,
            email="user@example.com",
        )

        response = app_client.get(f"/users/{AUTH_ID}")

        assert response.status_code == 200
        assert response.json() == {
            "id": user.id.value,
            "name": "Luna Reyes",
            "avatar": "https://example.com/avatar.jpg",
            "description": "Cantautora",
            "links": [],
        }

    def test_unknown_auth_id_returns_404(self):
        app_client = _client()
        app_client.app.dependency_overrides[get_current_user] = lambda: CurrentUser(
            auth_id=AUTH_ID,
            email="user@example.com",
        )

        response = app_client.get(f"/users/{AUTH_ID}")

        assert response.status_code == 404
        assert response.json() == {"detail": "El usuario no existe"}


class TestGetUserByName:
    def test_returns_public_profile(self):
        repo = FakeUserRepo()
        user = _named_user()
        repo.users_by_name[USERNAME] = user

        response = _client(repo).get(f"/users/name/{USERNAME}")

        assert response.status_code == 200
        assert response.json() == {
            "id": user.id.value,
            "name": "Luna Reyes",
            "avatar": "https://example.com/avatar.jpg",
            "description": "Cantautora",
            "links": [],
        }

    def test_unknown_name_returns_404(self):
        response = _client().get("/users/name/missing")

        assert response.status_code == 404
        assert response.json() == {"detail": "El usuario no existe"}


class TestUpdateUser:
    def test_missing_authorization_returns_401(self):
        response = _client().patch(
            f"/users/{AUTH_ID}",
            json={"name": "luna"},
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

        response = app_client.patch(
            f"/users/{OTHER_AUTH_ID}",
            json={"name": "luna"},
        )

        assert response.status_code == 404
        assert response.json() == {"detail": "El usuario no existe"}

    def test_updates_current_user_profile(self):
        repo = FakeUserRepo()
        user = User.create_empty()
        repo.users_by_auth_id[AUTH_ID] = user
        app_client = _client(repo)
        app_client.app.dependency_overrides[get_current_user] = lambda: CurrentUser(
            auth_id=AUTH_ID,
            email="user@example.com",
        )

        response = app_client.patch(
            f"/users/{AUTH_ID}",
            json={
                "name": "luna",
                "avatar": "https://example.com/avatar.jpg",
                "description": "Cantautora",
            },
        )

        assert response.status_code == 200
        assert response.json() == {
            "id": user.id.value,
            "name": "luna",
            "avatar": "https://example.com/avatar.jpg",
            "description": "Cantautora",
            "links": [],
        }

    def test_updates_current_user_profile_with_links(self):
        repo = FakeUserRepo()
        user = User.create_empty()
        repo.users_by_auth_id[AUTH_ID] = user
        app_client = _client(repo)
        app_client.app.dependency_overrides[get_current_user] = lambda: CurrentUser(
            auth_id=AUTH_ID,
            email="user@example.com",
        )

        response = app_client.patch(
            f"/users/{AUTH_ID}",
            json={
                "name": "luna",
                "links": [
                    {"url": "https://www.youtube.com/@luna"},
                    {"url": "https://example.com/luna"},
                ],
            },
        )

        assert response.status_code == 200
        body = response.json()
        assert body["name"] == "luna"
        assert len(body["links"]) == 2
        assert body["links"][0]["url"] == "https://www.youtube.com/@luna"
        assert body["links"][0]["type"] == "youtube"
        assert body["links"][0]["sort_index"] == 0
        assert body["links"][1]["type"] == "default"

    def test_unknown_auth_id_returns_404(self):
        app_client = _client()
        app_client.app.dependency_overrides[get_current_user] = lambda: CurrentUser(
            auth_id=AUTH_ID,
            email="user@example.com",
        )

        response = app_client.patch(
            f"/users/{AUTH_ID}",
            json={"name": "luna"},
        )

        assert response.status_code == 404
        assert response.json() == {"detail": "El usuario no existe"}

    def test_taken_name_returns_409(self):
        repo = FakeUserRepo()
        user = User.create_empty()
        taken = _named_user()
        repo.users_by_auth_id[AUTH_ID] = user
        repo.users_by_name["Luna Reyes"] = taken
        app_client = _client(repo)
        app_client.app.dependency_overrides[get_current_user] = lambda: CurrentUser(
            auth_id=AUTH_ID,
            email="user@example.com",
        )

        response = app_client.patch(
            f"/users/{AUTH_ID}",
            json={"name": "Luna Reyes"},
        )

        assert response.status_code == 409
        assert response.json() == {"detail": "Ese nombre ya está en uso"}
