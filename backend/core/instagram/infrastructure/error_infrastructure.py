from core.shared.infrastructure.infrastructure_error import InfrastructureError


class InstagramDbError(InfrastructureError):
    pass


class InstagramApiError(InfrastructureError):
    pass


class TokenDecryptError(InfrastructureError):
    pass
