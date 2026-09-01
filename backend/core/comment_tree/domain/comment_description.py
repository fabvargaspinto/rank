from backend.core.share.domain.string import String
from backend.core.comment_tree.domain.comment_error import CommentDescriptionTooLongError, CommentDescriptionTooShortError

MIN_LENGTH = 1
MAX_LENGTH = 230

class CommentDescription (String):
    def __init__(self, value: str):
        self.value = value
        self.validate()

    def validate(self):
        if len(self.value) < MIN_LENGTH:
            raise CommentDescriptionTooShortError(f"Comment description must be at least {MIN_LENGTH} characters long")
        if len(self.value) > MAX_LENGTH:
            raise CommentDescriptionTooLongError(f"Comment description must be at most {MAX_LENGTH} characters long")