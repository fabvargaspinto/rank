from datetime import UTC, datetime

from core.post.domain.post import Post
from core.post.domain.post_created_at import PostCreatedAt
from core.post.domain.post_id import PostId
from core.post.domain.post_link import PostLink
from core.post.domain.post_text import PostText
from core.post.infrastructure.post_mapper import PostMapper
from core.shared.domain.user_id import UserId

USER_ID = "550e8400-e29b-41d4-a716-446655440000"
POST_ID = "660e8400-e29b-41d4-a716-446655440000"
CREATED_AT = datetime(2026, 9, 22, 12, 0, 0, tzinfo=UTC)


def _mapper() -> PostMapper:
    return PostMapper()


def _post(link: str | None = "https://example.com/track") -> Post:
    return Post(
        id=PostId(POST_ID),
        user_id=UserId(USER_ID),
        text=PostText("Me encantó el último tema."),
        link=PostLink(link) if link else None,
        created_at=PostCreatedAt(CREATED_AT),
    )


class TestPostMapper:
    def test_to_row_uses_posts_columns(self):
        post = _post()

        row = _mapper().to_row(post)

        assert row == {
            "id": POST_ID,
            "user_id": USER_ID,
            "text": "Me encantó el último tema.",
            "link": "https://example.com/track",
            "created_at": post.created_at.to_isoformat(),
        }

    def test_to_row_keeps_link_null_when_missing(self):
        post = _post(link=None)

        row = _mapper().to_row(post)

        assert row["link"] is None

    def test_to_domain_rebuilds_post_from_row(self):
        mapper = _mapper()
        post = _post()

        rebuilt = mapper.to_domain(mapper.to_row(post))

        assert rebuilt.id.value == POST_ID
        assert rebuilt.user_id.value == USER_ID
        assert rebuilt.text.value == "Me encantó el último tema."
        assert rebuilt.link is not None
        assert rebuilt.link.value == "https://example.com/track"
        assert rebuilt.created_at.value == CREATED_AT

    def test_to_domain_keeps_link_none_when_null(self):
        rebuilt = _mapper().to_domain(
            {
                "id": POST_ID,
                "user_id": USER_ID,
                "text": "Hola",
                "link": None,
                "created_at": CREATED_AT.isoformat(),
            }
        )

        assert rebuilt.link is None
