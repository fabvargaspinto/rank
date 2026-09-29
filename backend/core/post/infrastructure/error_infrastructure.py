from core.shared.infrastructure.infrastructure_error import InfrastructureError


class PostLookupError(InfrastructureError):
    pass


class PostCreationError(InfrastructureError):
    pass


class PostDeletionError(InfrastructureError):
    pass
