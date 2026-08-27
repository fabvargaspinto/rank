from core.share.domain.domain_error import DomainError

class InvalidEmailError(DomainError):
    pass


class InvalidPasswordError(DomainError):
    pass


class InvalidProviderError(DomainError):
    pass


class InvalidUUIDError(DomainError):
    pass

class DuplicateAuthError(DomainError):
    pass