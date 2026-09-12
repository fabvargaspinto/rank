from core.shared.application.application_error import ApplicationError

class AuthAlreadyExistsError(ApplicationError):
    pass

class InvalidAuthProviderError(ApplicationError):
    pass

class InvalidAuthCredentialsError(ApplicationError):
    pass

class EmailAlreadyExistsError(ApplicationError):
    pass

class PasswordMismatchError(ApplicationError):
    pass

class EmailNotFoundError(ApplicationError):
    pass