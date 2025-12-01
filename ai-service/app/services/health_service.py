"""Health check service."""
from datetime import datetime

from app.core.config import settings
from app.core.logging import get_logger
from app.schemas.common_schemas import HealthResponse

logger = get_logger(__name__)


class HealthService:
    """Service for health check operations."""

    async def check_health(self) -> HealthResponse:
        """Check basic health status."""
        return HealthResponse(
            status="healthy",
            timestamp=datetime.utcnow(),
            version=settings.APP_VERSION,
            details={"service": "ai-service"},
        )

    async def check_readiness(self) -> HealthResponse:
        """Check if service is ready to accept requests."""
        details = {
            "service": "ai-service",
            "dependencies": {},
        }

        # TODO: Add dependency checks (VectorDB, LLM, etc.)

        return HealthResponse(
            status="healthy",
            timestamp=datetime.utcnow(),
            version=settings.APP_VERSION,
            details=details,
        )
