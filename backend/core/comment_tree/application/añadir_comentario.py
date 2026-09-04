from backend.core.comment_tree.domain.comment_tree import CommentTree
from backend.core.comment_tree.domain.comment_repository import CommentRepository
from datetime import datetime

class AñadirComentario:
    def __init__(self, comment_repository: CommentRepository):
        self.comment_repository = comment_repository

    def execute(self, user_id: str, comment: str, link: str):
        comment_tree = CommentTree.create(user_id, comment, link, datetime.now())

        self.comment_repository.add_comment(comment_tree)