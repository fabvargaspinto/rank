from backend.core.share.domain.domain_error import DomainError


class CommentDescriptionTooLongError(DomainError):
    pass

class CommentDescriptionTooShortError(DomainError):
    pass

class CommentTitleTooLongError(DomainError):
    pass

class CommentTitleTooShortError(DomainError):
    pass


class CommentLinkUrlInvalidError(DomainError):
    pass