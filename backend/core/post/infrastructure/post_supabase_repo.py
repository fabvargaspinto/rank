from core.post.domain.post import Post
from core.post.domain.post_page import PostCursor
from core.post.domain.post_repo import PostRepository
from core.post.infrastructure.error_infrastructure import (
    PostCreationError,
    PostDeletionError,
    PostLookupError,
)
from core.post.infrastructure.post_mapper import PostMapper
from core.shared.infrastructure.supabase_client import DBClient


class PostSupabaseRepo(PostRepository):
    def __init__(self, client: DBClient):
        self._db = client.get_db()
        self.mapper = PostMapper()

    def create_post(self, post: Post) -> Post:
        row = self.mapper.to_row(post)

        try:
            response = self._db.table("posts").insert(row).execute()
        except Exception as exc:
            raise PostCreationError("Error al crear la publicación") from exc

        rows = response.data or []
        if not rows or not isinstance(rows[0], dict):
            raise PostCreationError("Error al crear la publicación")

        return self.mapper.to_domain(rows[0])

    def get_posts_by_user_id(
        self,
        user_id: str,
        limit: int,
        cursor: PostCursor | None = None,
    ) -> list[Post]:
        if limit <= 0:
            return []

        try:
            query = (
                self._db.table("posts")
                .select("*")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .order("id", desc=True)
                .limit(limit)
            )
            if cursor is not None:
                query = query.or_(_cursor_filter(cursor))
            response = query.execute()
        except Exception as exc:
            raise PostLookupError("Error al buscar las publicaciones") from exc

        rows = response.data or []
        posts: list[Post] = []
        for row in rows:
            if not isinstance(row, dict):
                raise PostLookupError("Error al buscar las publicaciones")
            posts.append(self.mapper.to_domain(row))
        return posts

    def get_post(self, post_id: str) -> Post | None:
        try:
            response = (
                self._db.table("posts")
                .select("*")
                .eq("id", post_id)
                .limit(1)
                .execute()
            )
        except Exception as exc:
            raise PostLookupError("Error al buscar la publicación") from exc

        rows = response.data or []
        if not rows:
            return None
        row = rows[0]
        if not isinstance(row, dict):
            raise PostLookupError("Error al buscar la publicación")
        return self.mapper.to_domain(row)

    def delete_post(self, post_id: str) -> None:
        try:
            self._db.table("posts").delete().eq("id", post_id).execute()
        except Exception as exc:
            raise PostDeletionError("Error al borrar la publicación") from exc


def _cursor_filter(cursor: PostCursor) -> str:
    created_at = cursor.created_at.replace('"', "")
    return (
        f'created_at.lt."{created_at}",'
        f'and(created_at.eq."{created_at}",id.lt.{cursor.id})'
    )
