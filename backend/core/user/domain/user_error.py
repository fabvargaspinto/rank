from core.share.domain.domain_error import DomainError


class InvalidUserNameError(DomainError):
    pass

class InvalidUserDescriptionError(DomainError):
    pass

class InvalidUserAvatarUrlError(DomainError):
    pass

class InvalidUserCreatedAtError(DomainError):
    pass

class InvalidUserUpdatedAtError(DomainError):
    pass