class DomainError(Exception):
    pass

class InvalidStringError(DomainError):
    pass

class InvalidUUIDError(DomainError):
    pass

class InvalidURLError(DomainError):
    pass

class InvalidDateError(DomainError):
    pass