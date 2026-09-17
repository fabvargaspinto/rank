from core.user.domain.user import User
from core.user.domain.user_repo import UserRepository
from core.user.infrastructure.error_infrastructure import UserLookupError
from core.user.infrastructure.user_mapper import UserMapper
from db.db_client import DBClient


class UserSupabaseRepo(UserRepository):
    def __init__(self, client: DBClient):
        self._db = client.get_db()
        self.mapper = UserMapper()

    def get_user(self, user_id: str) -> User | None:
        return self._find_user("users", {"id": user_id})

    def get_user_by_auth_id(self, auth_id: str) -> User | None:
        try:
            response = (
                self._db.table("auth")
                .select("users(*)")
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
        return self._find_user("users", {"name": name})

    def _find_user(self, table: str, filters: dict) -> User | None:
        query = self._db.table(table).select("*")
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
