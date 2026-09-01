from backend.core.share.domain.string import String
from backend.core.comment_tree.domain.comment_error import CommentTitleTooLongError, CommentTitleTooShortError

MIN_LENGTH = 1
MAX_LENGTH = 50

class CommentTitle (String):
    def __init__(self, value: str):
        super().__init__(value)

    def validate(self):
        if len(self.value) < MIN_LENGTH:
            raise CommentTitleTooShortError(f"Comment title must be at least {MIN_LENGTH} characters long")
        if len(self.value) > MAX_LENGTH:
            raise CommentTitleTooLongError(f"Comment title must be at most {MAX_LENGTH} characters long")

    def __str__(self) -> str:
        return self.value