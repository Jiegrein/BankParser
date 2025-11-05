"""
Custom exception classes
Custom exception classes with status codes
"""


class AppException(Exception):
    """
    Base application exception
    Base exception for application-specific errors
    """

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str = None,
        details: dict = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or "INTERNAL_ERROR"
        self.details = details or {}
        super().__init__(self.message)


class NotFoundException(AppException):
    """
    Resource not found exception (404)
    Raised when a resource is not found
    """

    def __init__(self, message: str = "Resource not found", details: dict = None):
        super().__init__(
            message=message,
            status_code=404,
            error_code="NOT_FOUND",
            details=details,
        )


class BadRequestException(AppException):
    """
    Bad request exception (400)
    Raised for invalid request data
    """

    def __init__(self, message: str = "Bad request", details: dict = None):
        super().__init__(
            message=message,
            status_code=400,
            error_code="BAD_REQUEST",
            details=details,
        )


class UnauthorizedException(AppException):
    """
    Unauthorized exception (401)
    Raised when user is not authenticated
    """

    def __init__(self, message: str = "Unauthorized", details: dict = None):
        super().__init__(
            message=message,
            status_code=401,
            error_code="UNAUTHORIZED",
            details=details,
        )


class ForbiddenException(AppException):
    """
    Forbidden exception (403)
    User is authenticated but not authorized for this resource
    """

    def __init__(self, message: str = "Forbidden", details: dict = None):
        super().__init__(
            message=message,
            status_code=403,
            error_code="FORBIDDEN",
            details=details,
        )


class ConflictException(AppException):
    """
    Conflict exception (409)
    Resource already exists or state conflict
    """

    def __init__(self, message: str = "Conflict", details: dict = None):
        super().__init__(
            message=message,
            status_code=409,
            error_code="CONFLICT",
            details=details,
        )


class ValidationException(AppException):
    """
    Validation exception (422)
    Business logic validation failed
    """

    def __init__(self, message: str = "Validation failed", details: dict = None):
        super().__init__(
            message=message,
            status_code=422,
            error_code="VALIDATION_ERROR",
            details=details,
        )
