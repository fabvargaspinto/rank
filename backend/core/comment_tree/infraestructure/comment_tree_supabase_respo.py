from backend.core.comment_tree.domain.comment_repository import CommentRepository
from backend.core.comment_tree.domain.comment_tree import CommentTree
from backend.core.share.infraestructure.database.supabase_client import SupabaseClient

class CommentTreeSupabaseRepository(CommentRepository):
    def __init__(self, client: SupabaseClient):
        self.client = client.get_client()
        self.table_name = 'comment_tree'

    def add_comment(self, comment_tree: CommentTree):
        self.client.table(self.table_name).insert({
            'comment_id': comment_tree.comment_id.value,
            'user_id': comment_tree.user_id.value,
            'description': comment_tree.description.value,
            'link_url': comment_tree.link_url.value,
            'created_at': comment_tree.created_at.value,
        }).execute()