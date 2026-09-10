from core.shared.domain.domain_error import DomainError

class InvalidUserNameError(DomainError):
    pass

class InvalidUserAvatarError(DomainError):
    pass

class InvalidUserDescriptionError(DomainError):
    pass