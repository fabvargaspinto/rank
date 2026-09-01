from backend.core.share.domain.string import String
from backend.core.comment_tree.domain.comment_error import CommentLinkUrlInvalidError


MIN_LENGTH = 10
MAX_LENGTH = 2048

class CommentLinkUrl (String):
    def __init__(self, value: str):
        super().__init__(value)

    def validate(self):
        if not self.value.startswith("http"):
            raise CommentLinkUrlInvalidError(f"Comment link url must start with http")
        if len(self.value) > MAX_LENGTH:
            raise CommentLinkUrlInvalidError(f"Comment link url must be at most {MAX_LENGTH} characters long")
        if len(self.value) < MIN_LENGTH:
            raise CommentLinkUrlInvalidError(f"Comment link url must be at least {MIN_LENGTH} characters long")

    def __str__(self) -> str:
        return self.value