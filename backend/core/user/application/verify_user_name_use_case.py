from core.user.infraestructure.user_supabase_repo import UserSupabaseRepo
from core.user.domain.user_name import UserName
from core.user.application.error_application import UserNameAlreadyExistsError

class VerifyUserNameUseCase:
    def __init__(self, user_supabase_repo: UserSupabaseRepo):
        self.user_supabase_repo = user_supabase_repo


    def execute(self, name: str):
        user_name = UserName(name)
        result = self.user_supabase_repo.find_user_by_name(user_name.value)
        if result:
            raise UserNameAlreadyExistsError(f"User name {name} already exists")
        return True