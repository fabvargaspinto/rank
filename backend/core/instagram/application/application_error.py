from core.shared.application.application_error import ApplicationError


class InstagramNotConnectedError(ApplicationError):
    code = "INSTAGRAM_NOT_CONNECTED"


class InstagramOAuthDeniedError(ApplicationError):
    code = "INSTAGRAM_OAUTH_DENIED"


class InstagramOAuthStateError(ApplicationError):
    code = "INSTAGRAM_OAUTH_STATE"


class InstagramAccountAlreadyLinkedError(ApplicationError):
    code = "INSTAGRAM_ACCOUNT_LINKED"


class InstagramTokenExpiredError(ApplicationError):
    code = "INSTAGRAM_TOKEN_EXPIRED"


class InstagramGraphError(ApplicationError):
    code = "INSTAGRAM_UNAVAILABLE"
