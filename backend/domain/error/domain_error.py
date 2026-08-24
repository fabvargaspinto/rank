class DomainError(Exception):
    pass


class InvalidEmailError(DomainError):
    pass


class InvalidPasswordError(DomainError):
    pass


class InvalidProviderError(DomainError):
    pass


class InvalidDateError(DomainError):
    pass


class InvalidStringError(DomainError):
    pass

class InvalidDescriptionError(DomainError):
    pass

class InvalidURLError(DomainError):
    pass

class InvalidUserNameError(DomainError):
    pass