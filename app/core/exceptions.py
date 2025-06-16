"""Core exceptions for the application."""

class AppException(Exception):
    """Base exception for the application."""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class ValidationException(AppException):
    """Exception for validation errors."""
    def __init__(self, message: str):
        super().__init__(message, status_code=400)

class AuthenticationException(AppException):
    """Exception for authentication errors."""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401)

class AuthorizationException(AppException):
    """Exception for authorization errors."""
    def __init__(self, message: str = "Not authorized"):
        super().__init__(message, status_code=403)

class NotFoundException(AppException):
    """Exception for not found errors."""
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)

class ConflictException(AppException):
    """Exception for conflict errors."""
    def __init__(self, message: str = "Resource conflict"):
        super().__init__(message, status_code=409) 