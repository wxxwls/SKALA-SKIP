"""Custom exceptions and exception handlers."""
from typing import Any, Dict, Optional

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.logging import get_logger

logger = get_logger(__name__)


class BaseAppException(Exception):
    """Base exception for the application."""

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class ValidationException(BaseAppException):
    """Raised when request validation fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            code="VALIDATION_ERROR",
            message=message,
            status_code=422,
            details=details,
        )


class NotFoundException(BaseAppException):
    """Raised when a resource is not found."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            code="NOT_FOUND",
            message=message,
            status_code=404,
            details=details,
        )


class ExternalServiceException(BaseAppException):
    """Raised when an external service call fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            code="EXTERNAL_SERVICE_ERROR",
            message=message,
            status_code=502,
            details=details,
        )


class LLMException(BaseAppException):
    """Raised when LLM processing fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            code="LLM_ERROR",
            message=message,
            status_code=500,
            details=details,
        )


class VectorDBException(BaseAppException):
    """Raised when VectorDB operations fail."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            code="VECTORDB_ERROR",
            message=message,
            status_code=500,
            details=details,
        )


class ReportGenerationError(BaseAppException):
    """Raised when report generation fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            code="REPORT_GENERATION_ERROR",
            message=message,
            status_code=500,
            details=details,
        )


async def base_exception_handler(request: Request, exc: BaseAppException) -> JSONResponse:
    """Handle BaseAppException and return standardized error response."""
    logger.error(f"Application error: {exc.code} - {exc.message}", extra={"details": exc.details})
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.code,
            "message": exc.message,
            "details": exc.details,
        },
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    logger.exception(f"Unexpected error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred",
            "details": {},
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers to the FastAPI app."""
    app.add_exception_handler(BaseAppException, base_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
