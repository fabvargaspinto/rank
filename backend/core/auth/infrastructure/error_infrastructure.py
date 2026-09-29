from core.shared.infrastructure.infrastructure_error import InfrastructureError


class AuthCreationError(InfrastructureError):
    pass


class AuthLookupError(InfrastructureError):
    pass


class AuthDeletionError(InfrastructureError):
    pass


class EmailDecryptError(InfrastructureError):
    pass
