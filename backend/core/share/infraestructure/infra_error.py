class InfraError(Exception):
    pass


class DatabaseError(InfraError):
    pass


class EmailProtectorError(InfraError):
    pass


class AuthAlreadyExistsError(InfraError):
    pass
