from postgrest.exceptions import APIError

from core.shared.infrastructure.postgres_error import is_unique_violation
from core.shared.infrastructure.supabase_client import DBClient
from core.user.domain.user import User
from core.user.domain.user_error import (
    UsernameAlreadyTakenError,
    UserProfileNotFoundError,
)
from core.user.domain.user_repo import UserRepository
from core.user.infrastructure.error_infrastructure import (
    UserDeletionError,
    UserLookupError,
    UserUpdateError,
)
from core.user.infrastructure.user_mapper import UserMapper

USER_WITH_LINKS_SELECT = "*, user_links(*)"
AUTH_USER_WITH_LINKS_SELECT = "users(*, user_links(*))"


class UserSupabaseRepo(UserRepository):
    def __init__(self, client: DBClient):
        self._db = client.get_db()
        self.mapper = UserMapper()

    def get_user(self, user_id: str) -> User | None:
        return self._find_user({"id": user_id})

    def get_user_by_auth_id(self, auth_id: str) -> User | None:
        try:
            response = (
                self._db.table("auth")
                .select(AUTH_USER_WITH_LINKS_SELECT)
                .eq("id", auth_id)
                .limit(1)
                .execute()
            )
        except Exception as exc:
            raise UserLookupError("Error al buscar el usuario") from exc

        rows = response.data or []
        if not rows:
            return None

        user_row = self._embedded_user(rows[0])
        if user_row is None:
            return None
        return self.mapper.to_domain(user_row)

    def get_user_by_name(self, name: str) -> User | None:
        folded = name.strip().lower()
        pattern = folded.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        query = (
            self._db.table("users")
            .select(USER_WITH_LINKS_SELECT)
            .ilike("name", pattern)
            .limit(1)
        )

        try:
            response = query.execute()
        except Exception as exc:
            raise UserLookupError("Error al buscar el usuario") from exc

        rows = response.data or []
        if not rows:
            return None

        row = rows[0]
        if not isinstance(row, dict):
            raise UserLookupError("Error al buscar el usuario")
        return self.mapper.to_domain(row)

    def save(self, user: User) -> None:
        row = self.mapper.to_row(user)

        try:
            self._db.rpc(
                "update_profile",
                {
                    "p_user_id": row["id"],
                    "p_name": row["name"],
                    "p_display_name": row["display_name"],
                    "p_avatar_url": row["avatar_url"],
                    "p_description": row["description"],
                    "p_updated_at": row["updated_at"],
                    "p_links": self.mapper.links_to_rows(user),
                },
            ).execute()
        except APIError as exc:
            if is_unique_violation(exc):
                raise UsernameAlreadyTakenError("Ese nombre ya está en uso") from exc
            if str(exc.code) == "P0002":
                raise UserProfileNotFoundError("El usuario no existe") from exc
            raise UserUpdateError("Error al actualizar el usuario") from exc
        except Exception as exc:
            raise UserUpdateError("Error al actualizar el usuario") from exc

    def delete_user(self, user_id: str) -> None:
        try:
            self._db.table("users").delete().eq("id", user_id).execute()
        except Exception as exc:
            raise UserDeletionError("Error al borrar la cuenta") from exc

    def _find_user(self, filters: dict) -> User | None:
        query = self._db.table("users").select(USER_WITH_LINKS_SELECT)
        for column, value in filters.items():
            query = query.eq(column, value)

        try:
            response = query.limit(1).execute()
        except Exception as exc:
            raise UserLookupError("Error al buscar el usuario") from exc

        rows = response.data or []
        if not rows:
            return None

        row = rows[0]
        if not isinstance(row, dict):
            raise UserLookupError("Error al buscar el usuario")
        return self.mapper.to_domain(row)

    def _embedded_user(self, row: object) -> dict | None:
        if not isinstance(row, dict):
            raise UserLookupError("Error al buscar el usuario")

        user_row = row.get("users")
        if isinstance(user_row, list):
            if not user_row:
                return None
            user_row = user_row[0]
        if user_row is None:
            return None
        if not isinstance(user_row, dict):
            raise UserLookupError("Error al buscar el usuario")
        return user_row
