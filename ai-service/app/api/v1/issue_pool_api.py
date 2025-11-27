"""Issue Pool API endpoints."""
from typing import List

from fastapi import APIRouter, Depends

from app.schemas.issue_pool_schemas import (
    IssuePoolGenerateRequest,
    IssuePoolGenerateResponse,
    IssueRecommendRequest,
    IssueRecommendResponse,
)
from app.services.issue_pool_service import IssuePoolService

router = APIRouter()


def get_issue_pool_service() -> IssuePoolService:
    """Dependency injection for IssuePoolService."""
    return IssuePoolService()


@router.post("/generate", response_model=IssuePoolGenerateResponse)
async def generate_issue_pool(
    request: IssuePoolGenerateRequest,
    service: IssuePoolService = Depends(get_issue_pool_service),
) -> IssuePoolGenerateResponse:
    """Generate ESG issue pool based on input data."""
    return await service.generate_issues(request)


@router.post("/recommend", response_model=IssueRecommendResponse)
async def recommend_issues(
    request: IssueRecommendRequest,
    service: IssuePoolService = Depends(get_issue_pool_service),
) -> IssueRecommendResponse:
    """Recommend relevant ESG issues based on context."""
    return await service.recommend_issues(request)
