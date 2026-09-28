from core.shared.application.application_error import ApplicationError


class UserNotFoundError(ApplicationError):
    pass


class UserNameAlreadyExistsError(ApplicationError):
    code = "USERNAME_TAKEN"
    field = "name"


class InvalidAvatarFileError(ApplicationError):
    pass
