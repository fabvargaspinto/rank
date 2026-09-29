from io import BytesIO

from fastapi import FastAPI
from fastapi.testclient import TestClient
from PIL import Image

from api.dependencies.auth import (
    AuthJwtSettings,
    CurrentUser,
    get_auth_jwt_settings,
    get_current_user,
    get_jwks_client,
)
from config.dependency_container import (
    get_delete_account_use_case,
    get_public_profile_use_case,
    get_update_user_use_case,
    get_upload_avatar_use_case,
    get_user_use_case,
)
from controller.error_handlers import register_error_handlers
from controller.user_route import get_supabase_url, router
from core.comment.application.get_comments_by_user import GetCommentsByUser
from core.user.application.delete_account import DeleteAccount
from core.user.application.get_public_profile import GetPublicProfile
from core.user.application.get_user import GetUser
from core.user.application.get_user_by_name import GetUserByName
from core.user.application.update_user import UpdateUser
from core.user.application.upload_avatar import UploadAvatar
from core.user.domain.user import User
from core.user.infrastructure.avatar_url import public_avatar_url
from tests.unit.auth.application.fake_auth_repo import FakeAuthRepo
from tests.unit.comment.application.fake_comment_repo import FakeCommentRepo
from tests.unit.user.application.fake_avatar_storage import FakeAvatarStorage
from tests.unit.user.application.fake_user_repo import FakeUserRepo

AUTH_ID = "660e8400-e29b-41d4-a716-446655440000"
SUPABASE_URL = "https://example.supabase.co"
AVATAR_PATH = f"{AUTH_ID}/avatar.jpg"
AVATAR_URL = public_avatar_url(SUPABASE_URL, AVATAR_PATH)
ISSUER = "https://example.supabase.co/auth/v1"
USERNAME = "luna"


class _UnusedJwksClient:
    def get_signing_key_from_jwt(self, token: str):
        raise AssertionError("JWKS should not be used without a Bearer token")


def _named_user() -> User:
    user = User.create_empty()
    user.rename("lunareyes")
    user.change_display_name("Luna Reyes")
    user.change_avatar(AVATAR_PATH)
    user.describe("Cantautora")
    return user


def _client(repo: FakeUserRepo | None = None) -> TestClient:
    app = FastAPI()
    register_error_handlers(app)
    app.include_router(router)

    fake_repo = repo or FakeUserRepo()
    app.dependency_overrides[get_user_use_case] = lambda: GetUser(fake_repo)
    app.dependency_overrides[get_public_profile_use_case] = lambda: GetPublicProfile(
        GetUserByName(fake_repo),
        GetCommentsByUser(fake_repo, FakeCommentRepo()),
    )
    app.dependency_overrides[get_update_user_use_case] = lambda: UpdateUser(fake_repo)
    app.dependency_overrides[get_upload_avatar_use_case] = lambda: UploadAvatar(
        fake_repo, FakeAvatarStorage()
    )
    app.dependency_overrides[get_delete_account_use_case] = lambda: DeleteAccount(
        fake_repo, FakeAvatarStorage(), FakeAuthRepo()
    )
    app.dependency_overrides[get_auth_jwt_settings] = lambda: AuthJwtSettings(
        jwks_url=f"{ISSUER}/.well-known/jwks.json",
        issuer=ISSUER,
    )
    app.dependency_overrides[get_jwks_client] = lambda: _UnusedJwksClient()
    app.dependency_overrides[get_supabase_url] = lambda: SUPABASE_URL
    return TestClient(app)


class TestGetUserByAuthId:
    def test_missing_authorization_returns_401(self):
        response = _client().get("/me")

        assert response.status_code == 401
        assert response.json()["detail"] == "El token de autenticación no es válido"
        assert response.json()["code"] == "INVALID_AUTH_CREDENTIALS"

    def test_valid_current_user_returns_profile(self):
        repo = FakeUserRepo()
        user = _named_user()
        repo.users_by_auth_id[AUTH_ID] = user
        app_client = _client(repo)
        app_client.app.dependency_overrides[get_current_user] = lambda: CurrentUser(
            auth_id=AUTH_ID,
            email="user@example.com",
        )

        response = app_client.get("/me")

        assert response.status_code == 200
        assert response.json() == {
            "id": user.id.value,
            "name": "lunareyes",
            "display_name": "Luna Reyes",
            "avatar": AVATAR_URL,
            "description": "Cantautora",
            "links": [],
        }

    def test_unknown_auth_id_returns_404(self):
        app_client = _client()
        app_client.app.dependency_overrides[get_current_user] = lambda: CurrentUser(
            auth_id=AUTH_ID,
            email="user@example.com",
        )

        response = app_client.get("/me")

        assert response.status_code == 404
        assert response.json()["detail"] == "El usuario no existe"
        assert response.json()["code"] == "USER_NOT_FOUND"


class TestGetUserByName:
    def test_returns_public_profile(self):
        repo = FakeUserRepo()
        user = _named_user()
        repo.users_by_name[USERNAME] = user
        repo.users_by_id[user.id.value] = user

        response = _client(repo).get(f"/profiles/{USERNAME}")

        assert response.status_code == 200
        assert response.json() == {
            "id": user.id.value,
            "name": "lunareyes",
            "display_name": "Luna Reyes",
            "avatar": AVATAR_URL,
            "description": "Cantautora",
            "links": [],
            "comments": [],
            "next_cursor": None,
        }

    def test_unknown_name_returns_404(self):
        response = _client().get("/profiles/missing")

        assert response.status_code == 404
        assert response.json()["detail"] == "El usuario no existe"
        assert response.json()["code"] == "USER_NOT_FOUND"


class TestUpdateUser:
    def test_missing_authorization_returns_401(self):
        response = _client().patch(
            "/me",
            json={"name": "luna"},
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "El token de autenticación no es válido"
        assert response.json()["code"] == "INVALID_AUTH_CREDENTIALS"

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
            "/me",
            json={
                "name": "luna",
                "avatar": AVATAR_URL,
                "description": "Cantautora",
            },
        )

        assert response.status_code == 200
        assert response.json() == {
            "id": user.id.value,
            "name": "luna",
            "display_name": None,
            "avatar": AVATAR_URL,
            "description": "Cantautora",
            "links": [],
        }

    def test_rejects_avatar_from_another_domain(self):
        repo = FakeUserRepo()
        repo.users_by_auth_id[AUTH_ID] = User.create_empty()
        app_client = _client(repo)
        app_client.app.dependency_overrides[get_current_user] = lambda: CurrentUser(
            auth_id=AUTH_ID,
            email="user@example.com",
        )

        response = app_client.patch(
            "/me",
            json={
                "name": "luna",
                "avatar": "https://otro-dominio.example/pixel.gif",
            },
        )

        assert response.status_code == 400

    def test_omitted_avatar_keeps_existing(self):
        repo = FakeUserRepo()
        user = _named_user()
        repo.users_by_auth_id[AUTH_ID] = user
        repo.users_by_name["lunareyes"] = user
        app_client = _client(repo)
        app_client.app.dependency_overrides[get_current_user] = lambda: CurrentUser(
            auth_id=AUTH_ID,
            email="user@example.com",
        )

        response = app_client.patch(
            "/me",
            json={"name": "luna", "description": "Nueva bio"},
        )

        assert response.status_code == 200
        assert response.json()["avatar"] == AVATAR_URL
        assert response.json()["name"] == "luna"
        assert response.json()["description"] == "Nueva bio"

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
            "/me",
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
            "/me",
            json={"name": "luna"},
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "El usuario no existe"
        assert response.json()["code"] == "USER_NOT_FOUND"

    def test_taken_name_returns_409(self):
        repo = FakeUserRepo()
        user = User.create_empty()
        taken = _named_user()
        repo.users_by_auth_id[AUTH_ID] = user
        repo.users_by_name["lunareyes"] = taken
        app_client = _client(repo)
        app_client.app.dependency_overrides[get_current_user] = lambda: CurrentUser(
            auth_id=AUTH_ID,
            email="user@example.com",
        )

        response = app_client.patch(
            "/me",
            json={"name": "LunaReyes"},
        )

        assert response.status_code == 409
        body = response.json()
        assert body["request_id"]
        del body["request_id"]
        assert body == {
            "detail": "Ese nombre ya está en uso",
            "code": "USERNAME_TAKEN",
            "field": "name",
        }

    def test_reserved_name_returns_400(self):
        repo = FakeUserRepo()
        repo.users_by_auth_id[AUTH_ID] = User.create_empty()
        app_client = _client(repo)
        app_client.app.dependency_overrides[get_current_user] = lambda: CurrentUser(
            auth_id=AUTH_ID,
            email="user@example.com",
        )

        response = app_client.patch(
            "/me",
            json={"name": "Login"},
        )

        assert response.status_code == 400
        assert response.json()["code"] == "INVALID_USERNAME"
        assert response.json()["field"] == "name"


class TestUploadAvatar:
    def test_missing_authorization_returns_401(self):
        response = _client().put(
            "/me/avatar",
            files={"file": ("avatar.jpg", b"jpeg-bytes", "image/jpeg")},
        )

        assert response.status_code == 401

    def test_uploads_avatar_for_current_user(self):
        repo = FakeUserRepo()
        user = User.create_empty()
        repo.users_by_auth_id[AUTH_ID] = user
        app_client = _client(repo)
        app_client.app.dependency_overrides[get_current_user] = lambda: CurrentUser(
            auth_id=AUTH_ID,
            email="user@example.com",
        )

        image = BytesIO()
        Image.new("RGB", (8, 8), "red").save(image, format="PNG")

        response = app_client.put(
            "/me/avatar",
            files={"file": ("avatar.png", image.getvalue(), "image/png")},
        )

        assert response.status_code == 200
        assert response.json()["url"].startswith(
            public_avatar_url(SUPABASE_URL, f"{user.id.value}/")
        )
        assert response.json()["url"].endswith(".webp")

    def test_rejects_unsupported_type(self):
        repo = FakeUserRepo()
        repo.users_by_auth_id[AUTH_ID] = User.create_empty()
        app_client = _client(repo)
        app_client.app.dependency_overrides[get_current_user] = lambda: CurrentUser(
            auth_id=AUTH_ID,
            email="user@example.com",
        )

        gif = BytesIO()
        Image.new("RGB", (8, 8), "blue").save(gif, format="GIF")

        response = app_client.put(
            "/me/avatar",
            files={"file": ("avatar.gif", gif.getvalue(), "image/gif")},
        )

        assert response.status_code == 400
        assert response.json()["detail"] == "La imagen debe ser JPEG, PNG o WebP"
        assert response.json()["code"] == "INVALID_AVATAR_FILE"

    def test_limits_repeated_uploads_for_the_same_token(self):
        repo = FakeUserRepo()
        repo.users_by_auth_id[AUTH_ID] = User.create_empty()
        app_client = _client(repo)
        app_client.app.dependency_overrides[get_current_user] = lambda: CurrentUser(
            auth_id=AUTH_ID,
            email="user@example.com",
        )
        image = BytesIO()
        Image.new("RGB", (4, 4), "red").save(image, format="PNG")
        payload = image.getvalue()
        headers = {"Authorization": "Bearer avatar-rate-limit-token"}

        last = None
        for _ in range(11):
            last = app_client.put(
                "/me/avatar",
                headers=headers,
                files={"file": ("avatar.png", payload, "image/png")},
            )

        assert last is not None
        assert last.status_code == 429
        assert last.json()["code"] == "RATE_LIMITED"


class TestDeleteAccountRoute:
    def test_missing_authorization_returns_401(self):
        response = _client().delete("/me")

        assert response.status_code == 401
        assert response.json()["detail"] == "El token de autenticación no es válido"
        assert response.json()["code"] == "INVALID_AUTH_CREDENTIALS"

    def test_deletes_the_current_account(self):
        repo = FakeUserRepo()
        user = _named_user()
        repo.users_by_id[user.id.value] = user
        repo.users_by_auth_id[AUTH_ID] = user
        auth = FakeAuthRepo()
        avatars = FakeAvatarStorage()
        app_client = _client(repo)
        app_client.app.dependency_overrides[get_current_user] = lambda: CurrentUser(
            auth_id=AUTH_ID,
            email="user@example.com",
        )
        app_client.app.dependency_overrides[get_delete_account_use_case] = (
            lambda: DeleteAccount(repo, avatars, auth)
        )

        response = app_client.delete("/me")

        assert response.status_code == 204
        assert response.content == b""
        assert AUTH_ID not in repo.users_by_auth_id
        assert auth.deleted_ids == [AUTH_ID]
        assert avatars.deleted == [AVATAR_PATH]
