class DomainError(Exception):
    """Base class for domain-level errors."""


class UnauthorizedError(DomainError):
    def __init__(self, details: str | None = None) -> None:
        super().__init__("User not authorized")
        self.details = details


class UnavailableError(DomainError):
    def __init__(
        self,
        message: str | None = None,
        details: str | None = None,
        status: int | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.details = details
        self.status = status
