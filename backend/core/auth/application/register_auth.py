from core.user.domain.user import User
from core.auth.domain.auth import Auth
from core.auth.domain.auth_repo import AuthRepository
from core.auth.application.application_error import EmailAlreadyExistsError, PasswordMismatchError, InvalidAuthProviderError
from core.auth.domain.auth_provider import AuthProvider


class RegisterAuth:
    def __init__(self, auth_repo: AuthRepository):
        self.auth_repo = auth_repo



    def with_email(self, provider: AuthProvider, email: str, password: str, confirm_password: str ) -> "RegisterAuth":
        
        if provider.is_oauth():
            raise InvalidAuthProviderError("El proveedor de autenticación no es válido")
        
        if password != confirm_password:
            raise PasswordMismatchError("Las contraseñas no coinciden")

        if self.auth_repo.find_by_email(email):
            raise EmailAlreadyExistsError("El email ya está registrado")

        user = User.create_empty()    
        auth = Auth.create_with_email(user.id.value, email)
      
        return self.auth_repo.save(auth,user)



    def with_oauth(self, provider: AuthProvider, provider_id: str, email: str | None = None) -> "RegisterAuth":
        
        if provider.is_email():
            raise InvalidAuthProviderError("El proveedor de autenticación no es válido")

        if email and self.auth_repo.find_by_email(email):
            raise EmailAlreadyExistsError("El email ya está registrado")

        user = User.create_empty()    
        auth = Auth.create_with_oauth(user.id.value, provider, provider_id, email)      
        return self.auth_repo.save(auth,user)