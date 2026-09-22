from core.comment.domain.comment_id import CommentId
from core.shared.domain.domain_error import InvalidUUIDError

import pytest


class TestCommentId:

    def test_should_create_valid_id(self):
        value = "550e8400-e29b-41d4-a716-446655440000"

        comment_id = CommentId(value)

        assert comment_id.value == value

    def test_should_generate_id(self):
        comment_id = CommentId.generate()

        assert comment_id.value is not None

    def test_should_reject_invalid_id(self):
        with pytest.raises(InvalidUUIDError):
            CommentId("not-a-uuid")
