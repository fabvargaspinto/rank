from datetime import UTC, datetime

from core.user.domain.user import User
from core.user.infrastructure.user_supabase_repo import UserSupabaseRepo

USER_ID = "550e8400-e29b-41d4-a716-446655440000"
CREATED_AT = datetime(2026, 1, 2, 3, 4, 5, tzinfo=UTC).isoformat()


def _user_row(links: list[dict] | None = None) -> dict:
    return {
        "id": USER_ID,
        "name": "Luna Reyes",
        "avatar_url": "https://example.com/avatar.jpg",
        "description": "Cantautora",
        "created_at": CREATED_AT,
        "updated_at": CREATED_AT,
        "user_links": links or [],
    }


class _Result:
    def __init__(self, data):
        self.data = data


class _Query:
    def __init__(self, table: "_FakeSupabase", name: str):
        self._table = table
        self._name = name
        self.updated = None
        self.deleted = False
        self.inserted = None
        self._filters: dict = {}

    def select(self, *_args, **_kwargs):
        return self

    def eq(self, column, value):
        self._filters[column] = value
        return self

    def update(self, payload):
        self.updated = payload
        self._table.updated[self._name] = payload
        return self

    def delete(self):
        self.deleted = True
        self._table.deleted[self._name] = True
        return self

    def insert(self, rows):
        self.inserted = rows
        self._table.inserted[self._name] = rows
        return self

    def limit(self, *_args):
        return self

    def execute(self):
        data = self._table.data_for(self._name)
        if self.updated is not None and data:
            merged = [{**data[0], **self.updated}]
            self._table.set_data(self._name, merged)
            return _Result(merged)
        if self.deleted:
            self._table.set_data(self._name, [])
            return _Result([])
        if self.inserted is not None:
            self._table.set_data(self._name, list(self.inserted))
            return _Result(self.inserted)
        return _Result(data)


class _FakeSupabase:
    def __init__(self, users_data):
        self._tables = {
            "users": list(users_data),
            "auth": [{"users": users_data[0]}] if users_data else [],
            "user_links": list(users_data[0].get("user_links", [])) if users_data else [],
        }
        self.updated: dict = {}
        self.deleted: dict = {}
        self.inserted: dict = {}

    def table(self, name: str):
        return _Query(self, name)

    def data_for(self, name: str):
        if name == "auth":
            users = self._tables.get("users", [])
            if not users:
                return []
            user = {**users[0], "user_links": self._tables.get("user_links", [])}
            return [{"users": user}]
        if name == "users":
            users = self._tables.get("users", [])
            return [
                {**user, "user_links": self._tables.get("user_links", [])}
                for user in users
            ]
        return self._tables.get(name, [])

    def set_data(self, name: str, data):
        self._tables[name] = data


class _FakeDBClient:
    def __init__(self, data):
        self._client = _FakeSupabase(data)

    def get_db(self):
        return self._client


class TestUserSupabaseRepoJoin:
    def test_get_user_by_auth_id_reads_embedded_user(self):
        repo = UserSupabaseRepo(
            _FakeDBClient([_user_row()])
        )

        user = repo.get_user_by_auth_id("auth-id")

        assert user is not None
        assert user.id.value == USER_ID
        assert user.name is not None
        assert user.name.value == "Luna Reyes"
        assert user.avatar is not None
        assert user.avatar.value == "https://example.com/avatar.jpg"
        assert user.links == []

    def test_get_user_by_auth_id_reads_embedded_user_list(self):
        repo = UserSupabaseRepo(
            _FakeDBClient([_user_row()])
        )
        # list form still supported via mapper path on auth embed
        client = _FakeDBClient([])
        client._client._tables["auth"] = [{"users": [_user_row()]}]
        client._client._tables["users"] = [_user_row()]
        repo = UserSupabaseRepo(client)

        user = repo.get_user_by_auth_id("auth-id")

        assert user is not None
        assert user.id.value == USER_ID

    def test_get_user_by_auth_id_returns_none_when_join_is_empty(self):
        repo = UserSupabaseRepo(_FakeDBClient([]))

        assert repo.get_user_by_auth_id("auth-id") is None

    def test_get_user_loads_links(self):
        link_row = {
            "id": "660e8400-e29b-41d4-a716-446655440001",
            "user_id": USER_ID,
            "type": "youtube",
            "url": "https://www.youtube.com/@luna",
            "sort_index": 0,
        }
        repo = UserSupabaseRepo(_FakeDBClient([_user_row([link_row])]))

        user = repo.get_user(USER_ID)

        assert user is not None
        assert len(user.links) == 1
        assert user.links[0].url.value == "https://www.youtube.com/@luna"
        assert user.links[0].type.value == "youtube"


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
        assert client._client.updated["users"]["name"] == "luna"
        assert (
            client._client.updated["users"]["avatar_url"]
            == "https://example.com/avatar.jpg"
        )
        assert client._client.updated["users"]["description"] == "Cantautora"
        assert client._client.deleted.get("user_links") is True

    def test_update_user_persists_links(self):
        client = _FakeDBClient([_user_row()])
        repo = UserSupabaseRepo(client)
        user = repo.get_user(USER_ID)
        assert user is not None
        user.update_profile(name="luna")
        user.replace_links(["https://www.youtube.com/@luna"])

        updated = repo.update_user(user)

        assert updated is not None
        assert len(updated.links) == 1
        assert client._client.inserted["user_links"][0]["url"] == (
            "https://www.youtube.com/@luna"
        )
        assert client._client.inserted["user_links"][0]["type"] == "youtube"

    def test_update_user_returns_none_when_no_row(self):
        repo = UserSupabaseRepo(_FakeDBClient([]))
        user = User.create_empty()

        assert repo.update_user(user) is None
