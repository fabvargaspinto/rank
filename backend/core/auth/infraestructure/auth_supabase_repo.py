from datetime import datetime

from core.share.infraestructure.database.supabase_client import SupabaseClient
from core.share.infraestructure.infra_error import DatabaseError


class AuthSupabaseRepo:

    def __init__(self, supabase_client: SupabaseClient):
        self._client = supabase_client.get_client()
        self.table = "auth"

    def register(
        self,
        email: str,
        password: str,
        provider: str,
        name: str,
    ) -> None:

        print(
            email,
            password,
            provider,
            name,
            "email, password, provider, name",
        )

        now = datetime.now().isoformat()

        try:
            self._client.table(self.table).insert({
                "id": "01a044e1-6fe4-7294-af6e-0085309d753a",
                "name": name,
                "created_at": now,
                "updated_at": now,
            }).execute()

        except Exception as error:
            print(f"ERROR REGISTER AUTH REPO: {error!r}")
            raise DatabaseError(error)