from core.shared.infrastructure.infrastructure_error import InfrastructureError


class UserLookupError(InfrastructureError):
    pass


class UserUpdateError(InfrastructureError):
    pass


class AvatarUploadError(InfrastructureError):
    pass
