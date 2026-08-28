from core.user.infraestructure.user_supabase_repo import UserSupabaseRepo
from core.user.domain.user_name import UserName

class VerifyUserNameUseCase:
    def __init__(self, user_supabase_repo: UserSupabaseRepo):
        self.user_supabase_repo = user_supabase_repo


    def execute(self, name: str):
        user_name = UserName(name)
        result = self.user_supabase_repo.verify_user_name(user_name.value)
        return result