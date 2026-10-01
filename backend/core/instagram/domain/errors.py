from core.shared.domain.domain_error import DomainError


class InvalidInstagramAccountIdError(DomainError):
    code = "INVALID_INSTAGRAM_ACCOUNT"


class InvalidInstagramUsernameError(DomainError):
    code = "INVALID_INSTAGRAM_USERNAME"


class InvalidInstagramAvatarUrlError(DomainError):
    code = "INVALID_INSTAGRAM_AVATAR_URL"


class InvalidFollowersCountError(DomainError):
    code = "INVALID_FOLLOWERS_COUNT"


class InvalidInstagramTokenError(DomainError):
    code = "INVALID_INSTAGRAM_TOKEN"


class InvalidOAuthNonceError(DomainError):
    code = "INVALID_OAUTH_STATE"


class InstagramOAuthStateExpiredError(DomainError):
    code = "INSTAGRAM_OAUTH_EXPIRED"


class SnapshotWeekMismatchError(DomainError):
    code = "SNAPSHOT_WEEK_MISMATCH"
