from dataclasses import FrozenInstanceError

import pytest

from core.comment.domain.comment import Comment
from core.comment.domain.comment_error import (
    InvalidCommentLinkError,
    InvalidCommentTextError,
)
from core.shared.domain.domain_error import InvalidUUIDError

USER_ID = "550e8400-e29b-41d4-a716-446655440000"
COMMENT_TEXT = "Me encantó el último tema."
COMMENT_LINK = "https://example.com/track"


class TestComment:

    def test_should_create_comment(self):
        comment = Comment.create(
            user_id=USER_ID,
            text=COMMENT_TEXT,
        )

        assert comment.id.value is not None
        assert comment.user_id.value == USER_ID
        assert comment.text.value == COMMENT_TEXT
        assert comment.link is None
        assert comment.created_at is not None

    def test_should_create_comment_with_link(self):
        comment = Comment.create(
            user_id=USER_ID,
            text=COMMENT_TEXT,
            link=COMMENT_LINK,
        )

        assert comment.link is not None
        assert comment.link.value == COMMENT_LINK

    def test_should_generate_different_ids(self):
        first = Comment.create(
            user_id=USER_ID,
            text=COMMENT_TEXT,
        )
        second = Comment.create(
            user_id=USER_ID,
            text=COMMENT_TEXT,
        )

        assert first.id != second.id

    def test_should_reject_invalid_user_id(self):
        with pytest.raises(InvalidUUIDError):
            Comment.create(
                user_id="not-a-uuid",
                text=COMMENT_TEXT,
            )

    def test_should_reject_empty_text(self):
        with pytest.raises(InvalidCommentTextError):
            Comment.create(
                user_id=USER_ID,
                text="",
            )

    def test_should_reject_invalid_link(self):
        with pytest.raises(InvalidCommentLinkError):
            Comment.create(
                user_id=USER_ID,
                text=COMMENT_TEXT,
                link="http://example.com",
            )

    def test_should_be_immutable(self):
        comment = Comment.create(
            user_id=USER_ID,
            text=COMMENT_TEXT,
        )

        with pytest.raises(FrozenInstanceError):
            comment.text = comment.text
