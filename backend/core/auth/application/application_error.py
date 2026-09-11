from core.shared.application.application_error import ApplicationError

class AuthAlreadyExistsError(ApplicationError):
    pass

class InvalidAuthProviderError(ApplicationError):
    pass