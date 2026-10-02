import pytest

from core.post.domain.post_error import InvalidPostCursorError
from core.post.domain.post_page import PostCursor

POST_ID = "550e8400-e29b-41d4-a716-446655440000"


class TestPostCursor:
    def test_decode_normalizes_created_at(self):
        cursor = PostCursor.decode(f"2026-W01-1T00:00:00+00:00|{POST_ID}")

        assert cursor.created_at == "2025-12-29T00:00:00+00:00"
        assert cursor.id == POST_ID

    def test_decode_normalizes_zulu_suffix(self):
        cursor = PostCursor.decode(f"2026-09-22T12:00:00Z|{POST_ID}")

        assert cursor.created_at == "2026-09-22T12:00:00+00:00"

    def test_decode_rejects_invalid_cursor(self):
        for value in ("", "only-one-part", f"not-a-date|{POST_ID}", "2026-09-22T12:00:00+00:00|bad"):
            with pytest.raises(InvalidPostCursorError):
                PostCursor.decode(value)
