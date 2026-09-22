import pytest

from core.comment.domain.comment_error import InvalidCommentTextError
from core.comment.domain.comment_text import CommentText


class TestCommentText:

    def test_should_create_valid_text(self):
        text = CommentText("Me encantó el último tema.")

        assert text.value == "Me encantó el último tema."

    def test_should_reject_empty_text(self):
        with pytest.raises(InvalidCommentTextError):
            CommentText("")

    def test_should_accept_text_with_exactly_1_character(self):
        text = CommentText("A")

        assert text.value == "A"

    def test_should_accept_text_with_exactly_280_characters(self):
        value = "a" * 280

        text = CommentText(value)

        assert len(text.value) == 280

    def test_should_reject_text_longer_than_280_characters(self):
        value = "a" * 281

        with pytest.raises(InvalidCommentTextError):
            CommentText(value)

    def test_should_strip_external_spaces(self):
        text = CommentText("  Hola  ")

        assert text.value == "Hola"

    def test_should_preserve_internal_spaces(self):
        text = CommentText("Hola mundo")

        assert text.value == "Hola mundo"

    def test_should_reject_text_with_only_spaces(self):
        with pytest.raises(InvalidCommentTextError):
            CommentText("   ")
