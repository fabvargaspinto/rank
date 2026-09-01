from core.share.application.error_application import ErrorApplication

class UserNameAlreadyExistsError(ErrorApplication):
    pass

class UserNotFoundError(ErrorApplication):
    pass