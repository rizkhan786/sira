"""Custom exception classes for SIRA."""


class SIRAException(Exception):
    """Base exception for all SIRA errors."""

    def __init__(self, message: str, details: dict = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class LLMServiceError(SIRAException):
    """Raised when LLM service encounters an error."""

    pass


class DatabaseError(SIRAException):
    """Raised when database operations fail."""

    pass


class PatternStorageError(SIRAException):
    """Raised when pattern storage operations fail."""

    pass


class PatternRetrievalError(SIRAException):
    """Raised when pattern retrieval fails."""

    pass


class QualityScoreError(SIRAException):
    """Raised when quality scoring fails."""

    pass


class PatternExtractionError(SIRAException):
    """Raised when pattern extraction fails."""

    pass


class ConfigurationError(SIRAException):
    """Raised when configuration is invalid or missing."""

    pass


class ValidationError(SIRAException):
    """Raised when input validation fails."""

    pass
