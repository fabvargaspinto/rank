import pytest

from core.comment.domain.comment_error import InvalidCommentLinkError
from core.comment.domain.comment_link import CommentLink


class TestCommentLink:

    def test_should_create_valid_link(self):
        link = CommentLink("https://example.com/track")

        assert link.value == "https://example.com/track"

    def test_should_reject_http_link(self):
        with pytest.raises(InvalidCommentLinkError):
            CommentLink("http://example.com/track")

    def test_should_reject_link_without_https(self):
        with pytest.raises(InvalidCommentLinkError):
            CommentLink("example.com/track")

    def test_should_reject_empty_link(self):
        with pytest.raises(InvalidCommentLinkError):
            CommentLink("")

    def test_should_reject_link_with_only_spaces(self):
        with pytest.raises(InvalidCommentLinkError):
            CommentLink("   ")

    def test_should_accept_link_with_exactly_2048_characters(self):
        value = "https://" + ("a" * (2048 - 8))

        link = CommentLink(value)

        assert len(link.value) == 2048

    def test_should_reject_link_longer_than_2048_characters(self):
        value = "https://" + ("a" * (2049 - 8))

        with pytest.raises(InvalidCommentLinkError):
            CommentLink(value)

    def test_should_strip_external_spaces(self):
        link = CommentLink("https://example.com/track ")

        assert link.value == "https://example.com/track"

    def test_should_strip_leading_spaces(self):
        link = CommentLink(" https://example.com/track")

        assert link.value == "https://example.com/track"
