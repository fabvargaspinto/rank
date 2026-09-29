from dataclasses import FrozenInstanceError

import pytest

from core.post.domain.post import Post
from core.post.domain.post_error import (
    InvalidPostLinkError,
    InvalidPostTextError,
)
from core.shared.domain.domain_error import InvalidUUIDError

USER_ID = "550e8400-e29b-41d4-a716-446655440000"
POST_TEXT = "Me encantó el último tema."
POST_LINK = "https://example.com/track"


class TestPost:

    def test_should_create_post(self):
        post = Post.create(
            user_id=USER_ID,
            text=POST_TEXT,
        )

        assert post.id.value is not None
        assert post.user_id.value == USER_ID
        assert post.text.value == POST_TEXT
        assert post.link is None
        assert post.created_at is not None

    def test_should_create_post_with_link(self):
        post = Post.create(
            user_id=USER_ID,
            text=POST_TEXT,
            link=POST_LINK,
        )

        assert post.link is not None
        assert post.link.value == POST_LINK

    def test_should_generate_different_ids(self):
        first = Post.create(
            user_id=USER_ID,
            text=POST_TEXT,
        )
        second = Post.create(
            user_id=USER_ID,
            text=POST_TEXT,
        )

        assert first.id != second.id

    def test_should_reject_invalid_user_id(self):
        with pytest.raises(InvalidUUIDError):
            Post.create(
                user_id="not-a-uuid",
                text=POST_TEXT,
            )

    def test_should_reject_empty_text(self):
        with pytest.raises(InvalidPostTextError):
            Post.create(
                user_id=USER_ID,
                text="",
            )

    def test_should_reject_invalid_link(self):
        with pytest.raises(InvalidPostLinkError):
            Post.create(
                user_id=USER_ID,
                text=POST_TEXT,
                link="http://example.com",
            )

    def test_should_be_immutable(self):
        post = Post.create(
            user_id=USER_ID,
            text=POST_TEXT,
        )

        with pytest.raises(FrozenInstanceError):
            post.text = post.text
