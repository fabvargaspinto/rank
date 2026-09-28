from core.comment.domain.comment import Comment
from core.comment.domain.comment_repo import CommentRepository
from core.comment.infrastructure.comment_mapper import CommentMapper
from core.comment.infrastructure.error_infrastructure import (
    CommentCreationError,
    CommentDeletionError,
    CommentLookupError,
)
from db.db_client import DBClient


class CommentSupabaseRepo(CommentRepository):
    def __init__(self, client: DBClient):
        self._db = client.get_db()
        self.mapper = CommentMapper()

    def create_comment(self, comment: Comment) -> Comment:
        row = self.mapper.to_row(comment)

        try:
            response = self._db.table("comments").insert(row).execute()
        except Exception as exc:
            raise CommentCreationError("Error al crear el comentario") from exc

        rows = response.data or []
        if not rows or not isinstance(rows[0], dict):
            raise CommentCreationError("Error al crear el comentario")

        return self.mapper.to_domain(rows[0])

    def get_comments_by_user_id(
        self,
        user_id: str,
        limit: int,
        offset: int,
    ) -> list[Comment]:
        if limit <= 0:
            return []

        start = max(offset, 0)
        end = start + limit - 1

        try:
            response = (
                self._db.table("comments")
                .select("*")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .range(start, end)
                .execute()
            )
        except Exception as exc:
            raise CommentLookupError("Error al buscar los comentarios") from exc

        rows = response.data or []
        comments: list[Comment] = []
        for row in rows:
            if not isinstance(row, dict):
                raise CommentLookupError("Error al buscar los comentarios")
            comments.append(self.mapper.to_domain(row))
        return comments

    def get_comment(self, comment_id: str) -> Comment | None:
        try:
            response = (
                self._db.table("comments")
                .select("*")
                .eq("id", comment_id)
                .limit(1)
                .execute()
            )
        except Exception as exc:
            raise CommentLookupError("Error al buscar el comentario") from exc

        rows = response.data or []
        if not rows:
            return None
        row = rows[0]
        if not isinstance(row, dict):
            raise CommentLookupError("Error al buscar el comentario")
        return self.mapper.to_domain(row)

    def delete_comment(self, comment_id: str) -> None:
        try:
            self._db.table("comments").delete().eq("id", comment_id).execute()
        except Exception as exc:
            raise CommentDeletionError("Error al borrar el comentario") from exc
