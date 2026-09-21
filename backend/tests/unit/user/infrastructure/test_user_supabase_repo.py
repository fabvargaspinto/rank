from datetime import UTC, datetime

from core.user.domain.user import User
from core.user.infrastructure.user_supabase_repo import UserSupabaseRepo

USER_ID = "550e8400-e29b-41d4-a716-446655440000"
CREATED_AT = datetime(2026, 1, 2, 3, 4, 5, tzinfo=UTC).isoformat()


def _user_row() -> dict:
    return {
        "id": USER_ID,
        "name": "Luna Reyes",
        "avatar_url": "https://example.com/avatar.jpg",
        "description": "Cantautora",
        "created_at": CREATED_AT,
        "updated_at": CREATED_AT,
    }


class _Result:
    def __init__(self, data):
        self.data = data


class _Query:
    def __init__(self, data):
        self._data = data
        self.updated = None

    def select(self, *_args, **_kwargs):
        return self

    def eq(self, *_args, **_kwargs):
        return self

    def update(self, payload):
        self.updated = payload
        return self

    def limit(self, *_args):
        return self

    def execute(self):
        if self.updated is not None and self._data:
            return _Result([{**self._data[0], **self.updated}])
        return _Result(self._data)


class _FakeSupabase:
    def __init__(self, data):
        self._query = _Query(data)

    def table(self, _name: str):
        return self._query


class _FakeDBClient:
    def __init__(self, data):
        self._client = _FakeSupabase(data)

    def get_db(self):
        return self._client


class TestUserSupabaseRepoJoin:
    def test_get_user_by_auth_id_reads_embedded_user(self):
        repo = UserSupabaseRepo(
            _FakeDBClient([{"users": _user_row()}])
        )

        user = repo.get_user_by_auth_id("auth-id")

        assert user is not None
        assert user.id.value == USER_ID
        assert user.name is not None
        assert user.name.value == "Luna Reyes"
        assert user.avatar is not None
        assert user.avatar.value == "https://example.com/avatar.jpg"

    def test_get_user_by_auth_id_reads_embedded_user_list(self):
        repo = UserSupabaseRepo(
            _FakeDBClient([{"users": [_user_row()]}])
        )

        user = repo.get_user_by_auth_id("auth-id")

        assert user is not None
        assert user.id.value == USER_ID

    def test_get_user_by_auth_id_returns_none_when_join_is_empty(self):
        repo = UserSupabaseRepo(_FakeDBClient([]))

        assert repo.get_user_by_auth_id("auth-id") is None


class TestUserSupabaseRepoUpdate:
    def test_update_user_persists_profile_fields(self):
        client = _FakeDBClient([_user_row()])
        repo = UserSupabaseRepo(client)
        user = repo.get_user(USER_ID)
        assert user is not None
        user.update_profile(
            name="luna",
            avatar="https://example.com/avatar.jpg",
            description="Cantautora",
        )

        updated = repo.update_user(user)

        assert updated is not None
        assert updated.name is not None
        assert updated.name.value == "luna"
        assert client._client.table("users").updated["name"] == "luna"
        assert (
            client._client.table("users").updated["avatar_url"]
            == "https://example.com/avatar.jpg"
        )
        assert client._client.table("users").updated["description"] == "Cantautora"

    def test_update_user_returns_none_when_no_row(self):
        repo = UserSupabaseRepo(_FakeDBClient([]))
        user = User.create_empty()

        assert repo.update_user(user) is None
