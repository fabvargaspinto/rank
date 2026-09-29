import re
from datetime import UTC, datetime

from core.comment.domain.comment import Comment
from core.comment.infrastructure.comment_supabase_repo import CommentSupabaseRepo

USER_ID = "550e8400-e29b-41d4-a716-446655440000"
OTHER_USER_ID = "770e8400-e29b-41d4-a716-446655440000"
COMMENT_ID = "660e8400-e29b-41d4-a716-446655440000"
CREATED_AT = datetime(2026, 9, 22, 12, 0, 0, tzinfo=UTC).isoformat()
OLDER_CREATED_AT = datetime(2026, 9, 21, 12, 0, 0, tzinfo=UTC).isoformat()


def _comment_row(
    comment_id: str = COMMENT_ID,
    user_id: str = USER_ID,
    text: str = "Me encantó el último tema.",
    link: str | None = "https://example.com/track",
    created_at: str = CREATED_AT,
) -> dict:
    return {
        "id": comment_id,
        "user_id": user_id,
        "text": text,
        "link": link,
        "created_at": created_at,
    }


class _Result:
    def __init__(self, data):
        self.data = data


class _Query:
    def __init__(self, table: "_FakeSupabase", name: str):
        self._table = table
        self._name = name
        self._filters: dict = {}
        self._orders: list[tuple[str, bool]] = []
        self._limit: int | None = None
        self._or = ""
        self._inserted = None

    def select(self, *_args, **_kwargs):
        return self

    def eq(self, column, value):
        self._filters[column] = value
        return self

    def order(self, column, desc=False):
        self._orders.append((column, desc))
        return self

    def limit(self, count):
        self._limit = count
        return self

    def or_(self, filters):
        self._or = filters
        return self

    def insert(self, row):
        self._inserted = row
        self._table.inserted[self._name] = row
        return self

    def execute(self):
        if self._inserted is not None:
            self._table.append(self._name, self._inserted)
            return _Result([self._inserted])

        data = [
            row
            for row in self._table.data_for(self._name)
            if all(row.get(column) == value for column, value in self._filters.items())
        ]
        if self._orders:
            data = sorted(
                data,
                key=lambda row: tuple(row[column] for column, _desc in self._orders),
                reverse=all(desc for _column, desc in self._orders),
            )
        if self._or:
            match = re.search(
                r'created_at\.lt\."([^"]+)".*id\.lt\.([0-9a-fA-F-]+)',
                self._or,
            )
            if match:
                position = (match.group(1), match.group(2))
                data = [
                    row
                    for row in data
                    if (row["created_at"], row["id"]) < position
                ]
        if self._limit is not None:
            data = data[: self._limit]
        return _Result(data)


class _FakeSupabase:
    def __init__(self, comments_data):
        self._tables = {"comments": list(comments_data)}
        self.inserted: dict = {}

    def table(self, name: str):
        return _Query(self, name)

    def data_for(self, name: str):
        return self._tables.get(name, [])

    def append(self, name: str, row):
        self._tables.setdefault(name, []).append(row)


class _FakeDBClient:
    def __init__(self, data):
        self._client = _FakeSupabase(data)

    def get_db(self):
        return self._client


class TestCommentSupabaseRepoCreate:
    def test_create_comment_persists_row(self):
        client = _FakeDBClient([])
        repo = CommentSupabaseRepo(client)
        comment = Comment.create(
            user_id=USER_ID,
            text="Me encantó el último tema.",
            link="https://example.com/track",
        )

        created = repo.create_comment(comment)

        assert created.id.value == comment.id.value
        assert created.user_id.value == USER_ID
        assert created.text.value == "Me encantó el último tema."
        assert created.link is not None
        assert created.link.value == "https://example.com/track"
        assert client._client.inserted["comments"]["id"] == comment.id.value


class TestCommentSupabaseRepoGetByUser:
    def test_get_comments_by_user_id_returns_newest_first(self):
        repo = CommentSupabaseRepo(
            _FakeDBClient(
                [
                    _comment_row(
                        comment_id="660e8400-e29b-41d4-a716-446655440001",
                        text="Viejo",
                        created_at=OLDER_CREATED_AT,
                    ),
                    _comment_row(
                        comment_id="660e8400-e29b-41d4-a716-446655440002",
                        text="Nuevo",
                        created_at=CREATED_AT,
                    ),
                ]
            )
        )

        comments = repo.get_comments_by_user_id(USER_ID, limit=10)

        assert [comment.text.value for comment in comments] == ["Nuevo", "Viejo"]

    def test_get_comments_by_user_id_paginates(self):
        repo = CommentSupabaseRepo(
            _FakeDBClient(
                [
                    _comment_row(
                        comment_id="660e8400-e29b-41d4-a716-446655440001",
                        text="Primero",
                        created_at=CREATED_AT,
                    ),
                    _comment_row(
                        comment_id="660e8400-e29b-41d4-a716-446655440002",
                        text="Segundo",
                        created_at=OLDER_CREATED_AT,
                    ),
                ]
            )
        )

        first = repo.get_comments_by_user_id(USER_ID, limit=1)
        cursor = type("Cursor", (), {
            "created_at": first[0].created_at.to_isoformat(),
            "id": first[0].id.value,
        })()
        page = repo.get_comments_by_user_id(USER_ID, limit=1, cursor=cursor)

        assert len(page) == 1
        assert page[0].text.value == "Segundo"

    def test_get_comments_by_user_id_filters_other_users(self):
        repo = CommentSupabaseRepo(
            _FakeDBClient(
                [
                    _comment_row(text="Mio"),
                    _comment_row(
                        comment_id="660e8400-e29b-41d4-a716-446655440099",
                        user_id=OTHER_USER_ID,
                        text="Ajeno",
                    ),
                ]
            )
        )

        comments = repo.get_comments_by_user_id(USER_ID, limit=10)

        assert len(comments) == 1
        assert comments[0].text.value == "Mio"

    def test_get_comments_by_user_id_returns_empty_when_limit_is_zero(self):
        repo = CommentSupabaseRepo(_FakeDBClient([_comment_row()]))

        assert repo.get_comments_by_user_id(USER_ID, limit=0) == []
