from core.shared.domain.domain_error import DomainError


class InvalidPostTextError(DomainError):
    pass


class InvalidPostLinkError(DomainError):
    pass


class InvalidPostCursorError(DomainError):
    pass
