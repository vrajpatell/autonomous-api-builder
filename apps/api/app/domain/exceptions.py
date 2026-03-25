class DomainError(Exception):
    """Base class for domain/service layer exceptions."""

    code = "domain_error"

    def __init__(self, message: str, *, code: str | None = None, details: dict | None = None):
        super().__init__(message)
        self.message = message
        if code is not None:
            self.code = code
        self.details = details or {}


class ValidationDomainError(DomainError):
    code = "validation_error"


class AuthorizationDomainError(DomainError):
    code = "authorization_error"


class NotFoundDomainError(DomainError):
    code = "not_found"


class ConflictDomainError(DomainError):
    code = "conflict"
