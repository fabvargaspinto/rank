from core.shared.domain.domain_error import DomainError


class InvalidEmailError(DomainError):
    code = "INVALID_EMAIL"
    field = "email"


class InvalidAuthProviderError(DomainError):
    pass


class InvalidAuthProviderIdError(DomainError):
    pass


class IdentityAlreadyExistsError(DomainError):
    pass
