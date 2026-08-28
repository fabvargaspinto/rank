from core.share.infraestructure.database.supabase_client import SupabaseClient
from core.share.infraestructure.infra_error import DatabaseError
from core.user.infraestructure.error_infra import UserNameAlreadyExistsError


class UserSupabaseRepo:
    def __init__(self, supabase_client: SupabaseClient):
        self._client = supabase_client.get_client()
        self.table = "users"

    def verify_user_name(self, name: str):
        try:
            response = self._client.table(self.table).select("*").eq("name", name).execute()
            if response.data:
                raise UserNameAlreadyExistsError(f"User name {name} already exists")
            return None
        except UserNameAlreadyExistsError:
            raise
        except Exception as error:
            raise DatabaseError(f"Error verifying user name: {error!r}")