from core.shared.application.application_error import ApplicationError


class UserNotFoundError(ApplicationError):
    pass


class UserNameAlreadyExistsError(ApplicationError):
    pass


class InvalidAvatarFileError(ApplicationError):
    pass
