class DomainError(Exception):
    pass

class InvalidEmailError(DomainError):
    pass

class InvalidPasswordError(DomainError):
    pass

class InvalidProviderError(DomainError):
    pass