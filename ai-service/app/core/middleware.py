"""Custom middleware for FastAPI application."""
import time
import uuid
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.logging import get_logger

logger = get_logger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware to add unique request ID to each request."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id

        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log request/response information."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()

        request_id = getattr(request.state, "request_id", "unknown")

        logger.info(
            f"Request started | {request.method} {request.url.path} | "
            f"request_id={request_id}"
        )

        response = await call_next(request)

        process_time = time.time() - start_time

        logger.info(
            f"Request completed | {request.method} {request.url.path} | "
            f"status={response.status_code} | "
            f"duration={process_time:.3f}s | "
            f"request_id={request_id}"
        )

        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware to handle uncaught exceptions."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            return await call_next(request)
        except Exception as e:
            request_id = getattr(request.state, "request_id", "unknown")
            logger.error(
                f"Unhandled exception | {request.method} {request.url.path} | "
                f"error={str(e)} | request_id={request_id}"
            )
            raise
