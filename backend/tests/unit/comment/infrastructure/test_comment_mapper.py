from datetime import UTC, datetime

from core.comment.domain.comment import Comment
from core.comment.domain.comment_created_at import CommentCreatedAt
from core.comment.domain.comment_id import CommentId
from core.comment.domain.comment_link import CommentLink
from core.comment.domain.comment_text import CommentText
from core.comment.infrastructure.comment_mapper import CommentMapper
from core.user.domain.user_id import UserId

USER_ID = "550e8400-e29b-41d4-a716-446655440000"
COMMENT_ID = "660e8400-e29b-41d4-a716-446655440000"
CREATED_AT = datetime(2026, 9, 22, 12, 0, 0, tzinfo=UTC)


def _mapper() -> CommentMapper:
    return CommentMapper()


def _comment(link: str | None = "https://example.com/track") -> Comment:
    return Comment(
        id=CommentId(COMMENT_ID),
        user_id=UserId(USER_ID),
        text=CommentText("Me encantó el último tema."),
        link=CommentLink(link) if link else None,
        created_at=CommentCreatedAt(CREATED_AT),
    )


class TestCommentMapper:
    def test_to_row_uses_comments_columns(self):
        comment = _comment()

        row = _mapper().to_row(comment)

        assert row == {
            "id": COMMENT_ID,
            "user_id": USER_ID,
            "text": "Me encantó el último tema.",
            "link": "https://example.com/track",
            "created_at": comment.created_at.to_isoformat(),
        }

    def test_to_row_keeps_link_null_when_missing(self):
        comment = _comment(link=None)

        row = _mapper().to_row(comment)

        assert row["link"] is None

    def test_to_domain_rebuilds_comment_from_row(self):
        mapper = _mapper()
        comment = _comment()

        rebuilt = mapper.to_domain(mapper.to_row(comment))

        assert rebuilt.id.value == COMMENT_ID
        assert rebuilt.user_id.value == USER_ID
        assert rebuilt.text.value == "Me encantó el último tema."
        assert rebuilt.link is not None
        assert rebuilt.link.value == "https://example.com/track"
        assert rebuilt.created_at.value == CREATED_AT

    def test_to_domain_keeps_link_none_when_null(self):
        rebuilt = _mapper().to_domain(
            {
                "id": COMMENT_ID,
                "user_id": USER_ID,
                "text": "Hola",
                "link": None,
                "created_at": CREATED_AT.isoformat(),
            }
        )

        assert rebuilt.link is None
