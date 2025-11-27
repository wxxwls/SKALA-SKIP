"""Health check API endpoints."""
from fastapi import APIRouter, Depends

from app.schemas.common_schemas import HealthResponse
from app.services.health_service import HealthService

router = APIRouter()


def get_health_service() -> HealthService:
    """Dependency injection for HealthService."""
    return HealthService()


@router.get("/health", response_model=HealthResponse)
async def health_check(
    service: HealthService = Depends(get_health_service),
) -> HealthResponse:
    """Check the health status of the AI service."""
    return await service.check_health()


@router.get("/health/ready", response_model=HealthResponse)
async def readiness_check(
    service: HealthService = Depends(get_health_service),
) -> HealthResponse:
    """Check if the service is ready to accept requests."""
    return await service.check_readiness()
