# app/core/exceptions.py
class TalatriviaException(Exception):
    """Base exception for domain/application errors."""

    pass


# =========================
# DOMAIN EXCEPTIONS
# =========================
class ResourceNotFoundException(TalatriviaException):
    """Raised when a requested resource does not exist."""


class UnauthorizedException(TalatriviaException):
    """Raised when authentication or authorization fails."""


class ForbiddenException(TalatriviaException):
    """Raised when user lacks permissions."""


class BadRequestException(TalatriviaException):
    """Raised when request violates business rules."""


class ConflictException(TalatriviaException):
    """Raised when a business rule conflict occurs."""
