from core.user.infraestructure.user_supabase_repo import UserSupabaseRepo
from core.user.domain.user_name import UserName
from core.user.application.error_application import UserNotFoundError
from core.user.infraestructure.user_supabase_repo import User


class GetUserByNameUseCase:
    def __init__(self, user_supabase_repo: UserSupabaseRepo):
        self.user_supabase_repo = user_supabase_repo

    def execute(self, name: str):
        name = UserName(name)
        data = self.user_supabase_repo.get_user_by_name(name.value)
        if not data:
            raise UserNotFoundError(f"User {name} not found")

        user = User(
            id=data.id,
            name=data.name,
            avatar_url=data.avatar_url,
            description=data.description,
            created_at=data.created_at,
            updated_at=data.updated_at,
        )

        return user
