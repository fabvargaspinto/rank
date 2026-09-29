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
from config.dependency_container import (
    get_comments_by_user_use_case,
    get_create_comment_use_case,
    get_delete_comment_use_case,
    get_user_by_name_use_case,
    get_user_use_case,
)
from controller.comment_route import router
from controller.error_handlers import register_error_handlers
from core.comment.application.create_comment import CreateComment
from core.comment.application.delete_comment import DeleteComment
from core.comment.application.get_comments_by_user import GetCommentsByUser
from core.comment.domain.comment import Comment
from core.comment.domain.comment_created_at import CommentCreatedAt
from core.comment.domain.comment_id import CommentId
from core.comment.domain.comment_text import CommentText
from core.shared.domain.user_id import UserId
from core.user.application.get_user import GetUser
from core.user.application.get_user_by_name import GetUserByName
from core.user.domain.user import User
from tests.unit.comment.application.fake_comment_repo import FakeCommentRepo
from tests.unit.user.application.fake_user_repo import FakeUserRepo

AUTH_ID = "660e8400-e29b-41d4-a716-446655440000"
USER_ID = "550e8400-e29b-41d4-a716-446655440000"
USERNAME = "lunareyes"
ISSUER = "https://example.supabase.co/auth/v1"
BASE_TIME = datetime(2026, 9, 22, 12, 0, 0, tzinfo=UTC)


class _UnusedJwksClient:
    def get_signing_key_from_jwt(self, token: str):
        raise AssertionError("JWKS should not be used without a Bearer token")


def _comment(user_id: str, text: str, *, minutes_ago: int = 0) -> Comment:
    return Comment(
        id=CommentId.generate(),
        user_id=UserId(user_id),
        text=CommentText(text),
        link=None,
        created_at=CommentCreatedAt(BASE_TIME - timedelta(minutes=minutes_ago)),
    )


def _client(
    user_repo: FakeUserRepo | None = None,
    comment_repo: FakeCommentRepo | None = None,
) -> TestClient:
    app = FastAPI()
    register_error_handlers(app)
    app.include_router(router)

    fake_user_repo = user_repo or FakeUserRepo()
    fake_comment_repo = comment_repo or FakeCommentRepo()
    app.dependency_overrides[get_user_use_case] = lambda: GetUser(fake_user_repo)
    app.dependency_overrides[get_user_by_name_use_case] = lambda: GetUserByName(
        fake_user_repo
    )
    app.dependency_overrides[get_create_comment_use_case] = lambda: CreateComment(
        fake_comment_repo,
    )
    app.dependency_overrides[get_comments_by_user_use_case] = (
        lambda: GetCommentsByUser(fake_user_repo, fake_comment_repo)
    )
    app.dependency_overrides[get_delete_comment_use_case] = (
        lambda: DeleteComment(fake_comment_repo)
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
            "/me/posts",
            json={"text": "Hola"},
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "El token de autenticación no es válido"
        assert response.json()["code"] == "INVALID_AUTH_CREDENTIALS"

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
        assert len(comment_repo.comments) == 1

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


class TestListCommentsByUser:
    def test_lists_comments_for_user(self):
        user_repo = FakeUserRepo()
        comment_repo = FakeCommentRepo()
        user = User.create_empty()
        user.rename(USERNAME)
        user_repo.users_by_id[user.id.value] = user
        user_repo.users_by_name[USERNAME] = user
        comment_repo.create_comment(_comment(user.id.value, "Viejo", minutes_ago=10))
        comment_repo.create_comment(_comment(user.id.value, "Nuevo", minutes_ago=0))
        app_client = _client(user_repo, comment_repo)

        response = app_client.get(f"/profiles/{USERNAME}/posts")

        assert response.status_code == 200
        items = response.json()["items"]
        assert [item["text"] for item in items] == ["Nuevo", "Viejo"]

    def test_paginates_comments(self):
        user_repo = FakeUserRepo()
        comment_repo = FakeCommentRepo()
        user = User.create_empty()
        user.rename(USERNAME)
        user_repo.users_by_id[user.id.value] = user
        user_repo.users_by_name[USERNAME] = user
        comment_repo.create_comment(_comment(user.id.value, "Nuevo", minutes_ago=0))
        comment_repo.create_comment(_comment(user.id.value, "Viejo", minutes_ago=5))
        app_client = _client(user_repo, comment_repo)

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


class TestDeleteCommentRoute:
    def test_deletes_own_comment(self):
        user_repo = FakeUserRepo()
        comment_repo = FakeCommentRepo()
        user = User.create_empty()
        user_repo.users_by_auth_id[AUTH_ID] = user
        comment = _comment(user.id.value, "Un tema")
        comment_repo.create_comment(comment)
        app_client = _client(user_repo, comment_repo)
        app_client.app.dependency_overrides[get_current_user] = lambda: CurrentUser(
            auth_id=AUTH_ID,
            email="user@example.com",
        )

        response = app_client.delete(
            f"/me/posts/{comment.id.value}"
        )

        assert response.status_code == 204
        assert comment_repo.comments == []

    def test_other_users_comment_returns_404(self):
        user_repo = FakeUserRepo()
        comment_repo = FakeCommentRepo()
        user = User.create_empty()
        user_repo.users_by_auth_id[AUTH_ID] = user
        comment = _comment(USER_ID, "Ajeno")
        comment_repo.create_comment(comment)
        app_client = _client(user_repo, comment_repo)
        app_client.app.dependency_overrides[get_current_user] = lambda: CurrentUser(
            auth_id=AUTH_ID,
            email="user@example.com",
        )

        response = app_client.delete(
            f"/me/posts/{comment.id.value}"
        )

        assert response.status_code == 404
        assert comment_repo.comments == [comment]
