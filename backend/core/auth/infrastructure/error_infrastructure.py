from core.shared.infrastructure.infrastructure_error import InfrastructureError


class AuthCreationError(InfrastructureError):
    pass


class IdentityAlreadyExistsError(AuthCreationError):
    pass
