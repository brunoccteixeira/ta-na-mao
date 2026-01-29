"""Custom exceptions for the application."""

from typing import Any, Optional


class TaNaMaoException(Exception):
    """Base exception for Tá na Mão application."""
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[dict[str, Any]] = None,
    ):
        """Initialize exception.
        
        Args:
            message: Human-readable error message
            status_code: HTTP status code
            details: Additional error details
        """
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class NotFoundError(TaNaMaoException):
    """Resource not found exception."""
    
    def __init__(self, resource: str, identifier: str, details: Optional[dict[str, Any]] = None):
        """Initialize not found error.
        
        Args:
            resource: Resource type (e.g., "Program", "Municipality")
            identifier: Resource identifier
            details: Additional error details
        """
        message = f"{resource} with identifier '{identifier}' not found"
        super().__init__(message, status_code=404, details=details)


class ValidationError(TaNaMaoException):
    """Validation error exception."""
    
    def __init__(self, message: str, field: Optional[str] = None, details: Optional[dict[str, Any]] = None):
        """Initialize validation error.
        
        Args:
            message: Validation error message
            field: Field that failed validation
            details: Additional error details
        """
        if field:
            message = f"Validation error for field '{field}': {message}"
        super().__init__(message, status_code=400, details=details)


class ExternalAPIError(TaNaMaoException):
    """External API error exception."""
    
    def __init__(self, service: str, message: str, details: Optional[dict[str, Any]] = None):
        """Initialize external API error.
        
        Args:
            service: External service name (e.g., "IBGE", "Gemini")
            message: Error message
            details: Additional error details
        """
        message = f"Error calling {service} API: {message}"
        super().__init__(message, status_code=502, details=details)


class DatabaseError(TaNaMaoException):
    """Database error exception."""
    
    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        """Initialize database error.
        
        Args:
            message: Error message
            details: Additional error details
        """
        super().__init__(f"Database error: {message}", status_code=500, details=details)






