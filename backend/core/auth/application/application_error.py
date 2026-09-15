from core.shared.application.application_error import ApplicationError

class AuthAlreadyExistsError(ApplicationError):
    pass

class UnsupportedAuthProviderError(ApplicationError):
    pass

class InvalidAuthCredentialsError(ApplicationError):
    pass

class EmailAlreadyExistsError(ApplicationError):
    pass
