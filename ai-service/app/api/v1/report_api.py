"""Report API endpoints."""
from fastapi import APIRouter, Depends

from app.schemas.report_schemas import (
    ReportGenerateRequest,
    ReportGenerateResponse,
    ReportSectionRequest,
    ReportSectionResponse,
)
from app.services.report_service import ReportService

router = APIRouter()


def get_report_service() -> ReportService:
    """Dependency injection for ReportService."""
    return ReportService()


@router.post("/generate", response_model=ReportGenerateResponse)
async def generate_report(
    request: ReportGenerateRequest,
    service: ReportService = Depends(get_report_service),
) -> ReportGenerateResponse:
    """Generate ESG report draft."""
    return await service.generate_report(request)


@router.post("/section", response_model=ReportSectionResponse)
async def generate_section(
    request: ReportSectionRequest,
    service: ReportService = Depends(get_report_service),
) -> ReportSectionResponse:
    """Generate a specific section of the ESG report."""
    return await service.generate_section(request)
