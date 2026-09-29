import pytest

from core.post.domain.post_error import InvalidPostLinkError
from core.post.domain.post_link import PostLink


class TestPostLink:

    def test_should_create_valid_link(self):
        link = PostLink("https://example.com/track")

        assert link.value == "https://example.com/track"

    def test_should_reject_http_link(self):
        with pytest.raises(InvalidPostLinkError):
            PostLink("http://example.com/track")

    def test_should_reject_link_without_https(self):
        with pytest.raises(InvalidPostLinkError):
            PostLink("example.com/track")

    def test_should_reject_empty_link(self):
        with pytest.raises(InvalidPostLinkError):
            PostLink("")

    def test_should_reject_link_without_host(self):
        with pytest.raises(InvalidPostLinkError):
            PostLink("https://")

    def test_should_reject_link_with_only_spaces(self):
        with pytest.raises(InvalidPostLinkError):
            PostLink("   ")

    def test_should_accept_link_with_exactly_2048_characters(self):
        value = "https://" + ("a" * (2048 - 8))

        link = PostLink(value)

        assert len(link.value) == 2048

    def test_should_reject_link_longer_than_2048_characters(self):
        value = "https://" + ("a" * (2049 - 8))

        with pytest.raises(InvalidPostLinkError):
            PostLink(value)

    def test_should_strip_external_spaces(self):
        link = PostLink("https://example.com/track ")

        assert link.value == "https://example.com/track"

    def test_should_strip_leading_spaces(self):
        link = PostLink(" https://example.com/track")

        assert link.value == "https://example.com/track"
