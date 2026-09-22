from core.shared.domain.domain_error import DomainError


class InvalidUserNameError(DomainError):
    pass

class InvalidUserAvatarError(DomainError):
    pass

class InvalidUserDescriptionError(DomainError):
    pass

class InvalidUserLinkTypeError(DomainError):
    pass

class InvalidUserLinkUrlError(DomainError):
    pass

class InvalidUserLinkSortIndexError(DomainError):
    pass

class TooManyUserLinksError(DomainError):
    pass

class UserLinkNotFoundError(DomainError):
    pass

class InvalidUserLinksReorderError(DomainError):
    pass
