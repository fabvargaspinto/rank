from backend.core.comment_tree.domain.comment_tree import CommentTree
from typing import Protocol

class CommentRepository(Protocol):
    def add_comment(self, comment_tree: CommentTree):
        pass