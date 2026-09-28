from core.shared.domain.domain_error import DomainError


class InvalidEmailError(DomainError):
    pass


class InvalidAuthProviderError(DomainError):
    pass


class InvalidAuthProviderIdError(DomainError):
    pass


class IdentityAlreadyExistsError(DomainError):
    pass
