from datetime import datetime
from pydantic import BaseModel
from core.share.infraestructure.database.supabase_client import SupabaseClient
from core.share.infraestructure.infra_error import DatabaseError
from core.user.infraestructure.error_infra import UserNameAlreadyExistsError, UserNotFoundError


class User(BaseModel):
    id: str
    name: str
    avatar_url: str | None = None
    description: str | None = None
    created_at: datetime
    updated_at: datetime


class UserSupabaseRepo:
    def __init__(self, supabase_client: SupabaseClient):
        self._client = supabase_client.get_client()
        self.table = "users"

    def find_user_by_name(self, name: str):
        try:
            response = self._client.table(self.table).select("*").eq("name", name).execute()
            if response.data:
                return response.data[0]
        except Exception as error:
            raise DatabaseError(f"Error finding user by name: {error!r}")

    def get_user_by_name(self, name: str):
        try:
            response = self._client.table(self.table).select("id, name,avatar_url, description, created_at, updated_at").eq("name", name).execute()
            if response.data:
                return User(**response.data[0])
            raise UserNotFoundError(f"User {name} not found")
        except Exception as error:
            raise DatabaseError(f"Error getting user by name: {error!r}")