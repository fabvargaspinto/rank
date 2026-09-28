class DomainError(Exception):
    pass

class InvalidUUIDError(DomainError):
    pass

class InvalidDateError(DomainError):
    pass

class InvalidStringError(DomainError):
    pass


class InvalidHttpsUrlError(DomainError):
    pass
