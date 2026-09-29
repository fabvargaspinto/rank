class DomainError(Exception):
    pass

class InvalidUUIDError(DomainError):
    code = "INVALID_ID"

class InvalidDateError(DomainError):
    pass

class InvalidStringError(DomainError):
    pass


class InvalidHttpsUrlError(DomainError):
    pass
