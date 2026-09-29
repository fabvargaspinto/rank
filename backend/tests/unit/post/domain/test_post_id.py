import pytest

from core.post.domain.post_id import PostId
from core.shared.domain.domain_error import InvalidUUIDError


class TestPostId:

    def test_should_create_valid_id(self):
        value = "550e8400-e29b-41d4-a716-446655440000"

        post_id = PostId(value)

        assert post_id.value == value

    def test_should_generate_id(self):
        post_id = PostId.generate()

        assert post_id.value is not None

    def test_should_reject_invalid_id(self):
        with pytest.raises(InvalidUUIDError):
            PostId("not-a-uuid")
