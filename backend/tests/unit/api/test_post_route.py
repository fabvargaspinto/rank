from datetime import UTC, datetime, timedelta

from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.dependencies.auth import (
    AuthJwtSettings,
    CurrentUser,
    get_auth_jwt_settings,
    get_current_user,
    get_jwks_client,
)
from api.dependencies.container import (
    get_create_post_use_case,
    get_delete_post_use_case,
    get_posts_by_user_use_case,
    get_user_by_name_use_case,
    get_user_use_case,
)
from api.errors import register_error_handlers
from api.routers.me import router as me_router
from api.routers.profiles import router as profiles_router
from core.post.application.create_post import CreatePost
from core.post.application.delete_post import DeletePost
from core.post.application.get_posts_by_user import GetPostsByUser
from core.post.domain.post import Post
from core.post.domain.post_created_at import PostCreatedAt
from core.post.domain.post_id import PostId
from core.post.domain.post_text import PostText
from core.shared.domain.user_id import UserId
from core.user.application.get_user import GetUser
from core.user.application.get_user_by_name import GetUserByName
from core.user.domain.user import User
from tests.unit.post.application.fake_post_repo import FakePostRepo
from tests.unit.user.application.fake_user_repo import FakeUserRepo

AUTH_ID = "660e8400-e29b-41d4-a716-446655440000"
USER_ID = "550e8400-e29b-41d4-a716-446655440000"
USERNAME = "lunareyes"
ISSUER = "https://example.supabase.co/auth/v1"
BASE_TIME = datetime(2026, 9, 22, 12, 0, 0, tzinfo=UTC)


class _UnusedJwksClient:
    def get_signing_key_from_jwt(self, token: str):
        raise AssertionError("JWKS should not be used without a Bearer token")


def _post(user_id: str, text: str, *, minutes_ago: int = 0) -> Post:
    return Post(
        id=PostId.generate(),
        user_id=UserId(user_id),
        text=PostText(text),
        link=None,
        created_at=PostCreatedAt(BASE_TIME - timedelta(minutes=minutes_ago)),
    )


def _client(
    user_repo: FakeUserRepo | None = None,
    post_repo: FakePostRepo | None = None,
) -> TestClient:
    app = FastAPI()
    register_error_handlers(app)
    app.include_router(me_router)
    app.include_router(profiles_router)

    fake_user_repo = user_repo or FakeUserRepo()
    fake_post_repo = post_repo or FakePostRepo()
    app.dependency_overrides[get_user_use_case] = lambda: GetUser(fake_user_repo)
    app.dependency_overrides[get_user_by_name_use_case] = lambda: GetUserByName(
        fake_user_repo
    )
    app.dependency_overrides[get_create_post_use_case] = lambda: CreatePost(
        fake_post_repo,
    )
    app.dependency_overrides[get_posts_by_user_use_case] = lambda: GetPostsByUser(
        fake_user_repo, fake_post_repo
    )
    app.dependency_overrides[get_delete_post_use_case] = lambda: DeletePost(
        fake_post_repo
    )
    app.dependency_overrides[get_auth_jwt_settings] = lambda: AuthJwtSettings(
        jwks_url=f"{ISSUER}/.well-known/jwks.json",
        issuer=ISSUER,
    )
    app.dependency_overrides[get_jwks_client] = lambda: _UnusedJwksClient()
    return TestClient(app)


class TestCreatePost:
    def test_missing_authorization_returns_401(self):
        response = _client().post(
            "/me/posts",
            json={"text": "Hola"},
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "El token de autenticación no es válido"
        assert response.json()["code"] == "INVALID_AUTH_CREDENTIALS"

    def test_creates_post_for_current_user(self):
        user_repo = FakeUserRepo()
        post_repo = FakePostRepo()
        user = User.create_empty()
        user_repo.users_by_auth_id[AUTH_ID] = user
        app_client = _client(user_repo, post_repo)
        app_client.app.dependency_overrides[get_current_user] = lambda: CurrentUser(
            auth_id=AUTH_ID,
            email="user@example.com",
        )

        response = app_client.post(
            "/me/posts",
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
        assert len(post_repo.posts) == 1

    def test_unknown_auth_id_returns_404(self):
        app_client = _client()
        app_client.app.dependency_overrides[get_current_user] = lambda: CurrentUser(
            auth_id=AUTH_ID,
            email="user@example.com",
        )

        response = app_client.post(
            "/me/posts",
            json={"text": "Hola"},
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "El usuario no existe"
        assert response.json()["code"] == "USER_NOT_FOUND"

    def test_invalid_text_returns_400(self):
        user_repo = FakeUserRepo()
        user_repo.users_by_auth_id[AUTH_ID] = User.create_empty()
        app_client = _client(user_repo)
        app_client.app.dependency_overrides[get_current_user] = lambda: CurrentUser(
            auth_id=AUTH_ID,
            email="user@example.com",
        )

        response = app_client.post(
            "/me/posts",
            json={"text": "   "},
        )

        assert response.status_code == 400


class TestListPostsByUser:
    def test_lists_posts_for_user(self):
        user_repo = FakeUserRepo()
        post_repo = FakePostRepo()
        user = User.create_empty()
        user.rename(USERNAME)
        user_repo.users_by_id[user.id.value] = user
        user_repo.users_by_name[USERNAME] = user
        post_repo.create_post(_post(user.id.value, "Viejo", minutes_ago=10))
        post_repo.create_post(_post(user.id.value, "Nuevo", minutes_ago=0))
        app_client = _client(user_repo, post_repo)

        response = app_client.get(f"/profiles/{USERNAME}/posts")

        assert response.status_code == 200
        items = response.json()["items"]
        assert [item["text"] for item in items] == ["Nuevo", "Viejo"]

    def test_paginates_posts(self):
        user_repo = FakeUserRepo()
        post_repo = FakePostRepo()
        user = User.create_empty()
        user.rename(USERNAME)
        user_repo.users_by_id[user.id.value] = user
        user_repo.users_by_name[USERNAME] = user
        post_repo.create_post(_post(user.id.value, "Nuevo", minutes_ago=0))
        post_repo.create_post(_post(user.id.value, "Viejo", minutes_ago=5))
        app_client = _client(user_repo, post_repo)

        first = app_client.get(
            f"/profiles/{USERNAME}/posts",
            params={"limit": 1},
        )
        cursor = first.json()["next_cursor"]

        response = app_client.get(
            f"/profiles/{USERNAME}/posts",
            params={"limit": 1, "cursor": cursor},
        )

        assert response.status_code == 200
        items = response.json()["items"]
        assert len(items) == 1
        assert items[0]["text"] == "Viejo"

    def test_invalid_post_id_returns_422(self):
        user_repo = FakeUserRepo()
        user_repo.users_by_auth_id[AUTH_ID] = User.create_empty()
        app_client = _client(user_repo)
        app_client.app.dependency_overrides[get_current_user] = lambda: CurrentUser(
            auth_id=AUTH_ID,
            email="user@example.com",
        )

        response = app_client.delete("/me/posts/not-a-uuid")

        assert response.status_code == 422
        assert response.json()["code"] == "INVALID_ID"

    def test_invalid_username_returns_400(self):
        response = _client().get("/profiles/no/posts")

        assert response.status_code == 400
        assert response.json()["code"] == "INVALID_USERNAME"

    def test_unknown_user_returns_404(self):
        response = _client().get(f"/profiles/{USERNAME}/posts")

        assert response.status_code == 404
        assert response.json()["detail"] == "El usuario no existe"
        assert response.json()["code"] == "USER_NOT_FOUND"


class TestDeletePostRoute:
    def test_deletes_own_post(self):
        user_repo = FakeUserRepo()
        post_repo = FakePostRepo()
        user = User.create_empty()
        user_repo.users_by_auth_id[AUTH_ID] = user
        post = _post(user.id.value, "Un tema")
        post_repo.create_post(post)
        app_client = _client(user_repo, post_repo)
        app_client.app.dependency_overrides[get_current_user] = lambda: CurrentUser(
            auth_id=AUTH_ID,
            email="user@example.com",
        )

        response = app_client.delete(f"/me/posts/{post.id.value}")

        assert response.status_code == 204
        assert post_repo.posts == []

    def test_other_users_post_returns_404(self):
        user_repo = FakeUserRepo()
        post_repo = FakePostRepo()
        user = User.create_empty()
        user_repo.users_by_auth_id[AUTH_ID] = user
        post = _post(USER_ID, "Ajeno")
        post_repo.create_post(post)
        app_client = _client(user_repo, post_repo)
        app_client.app.dependency_overrides[get_current_user] = lambda: CurrentUser(
            auth_id=AUTH_ID,
            email="user@example.com",
        )

        response = app_client.delete(f"/me/posts/{post.id.value}")

        assert response.status_code == 404
        assert post_repo.posts == [post]
