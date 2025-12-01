"""
Media Analysis API Router

Endpoints for ESG news collection, sentiment analysis, and issue classification.

IMPORTANT: These are internal APIs called only by Spring Boot, not by the frontend.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, status, Query
from pydantic import BaseModel, Field

from app.core.logging import get_logger
from app.schemas.common_schema import APIResponse
from app.services.media_analysis_service import (
    MediaAnalysisService,
    get_media_analysis_service,
)

logger = get_logger(__name__)

# Create router with prefix
router = APIRouter(
    prefix="/internal/v1/media",
    tags=["미디어 분석"],
)


# ============ Request/Response Schemas ============

class AnalyzeNewsRequest(BaseModel):
    """Request to analyze news for given keywords"""
    keywords: List[str] = Field(
        ...,
        min_length=1,
        max_length=10,
        description="Search keywords (max 10)"
    )
    max_pages: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Max pages per keyword (1-10)"
    )


class ArticleResponse(BaseModel):
    """Single news article response"""
    title: str
    clean_title: str
    description: str
    clean_description: str
    link: str
    originallink: Optional[str] = None
    pubDate: str
    esg_issues: List[str]
    esg_categories: List[str]
    sentiment: str
    sentiment_score: float
    positive_count: int
    negative_count: int


class IssueStatistic(BaseModel):
    """ESG issue statistics"""
    issue: str
    count: int
    percentage: float
    esg_category: str


class SentimentStatistic(BaseModel):
    """Sentiment statistics"""
    positive: int = Field(alias="긍정")
    negative: int = Field(alias="부정")
    neutral: int = Field(alias="중립")
    avg_score: float

    class Config:
        populate_by_name = True


class CategoryStatistic(BaseModel):
    """ESG category statistics"""
    E: int
    S: int
    G: int
    ETC: int


class AnalysisStatistics(BaseModel):
    """Complete analysis statistics"""
    issue_statistics: List[IssueStatistic]
    sentiment_statistics: dict
    category_statistics: CategoryStatistic


class AnalyzeNewsResponse(BaseModel):
    """Response for news analysis"""
    total_collected: int
    unique_articles: int
    articles: List[ArticleResponse]
    statistics: AnalysisStatistics


class SearchArticlesRequest(BaseModel):
    """Request to search within analyzed articles"""
    keyword: str = Field(..., min_length=1, description="Search keyword")


class SearchArticlesResponse(BaseModel):
    """Response for article search"""
    keyword: str
    count: int
    articles: List[ArticleResponse]


class IssueArticlesResponse(BaseModel):
    """Response for articles by ESG issue"""
    issue: str
    count: int
    articles: List[ArticleResponse]


# ============ API Endpoints ============

@router.get(
    "",
    response_model=APIResponse[AnalyzeNewsResponse],
    status_code=status.HTTP_200_OK,
    summary="미디어 분석 데이터 조회",
    description="""
저장된/캐시된 미디어 분석 데이터를 조회합니다.

키워드 없이 사전 분석된 미디어 데이터를 반환합니다.
최초 분석은 POST /analyze 엔드포인트를 사용하세요.
""",
)
async def get_media_data(
    service: MediaAnalysisService = Depends(get_media_analysis_service),
) -> APIResponse[AnalyzeNewsResponse]:
    """
    Get stored media analysis data.

    Returns:
        APIResponse with analysis results
    """
    logger.info("GET /internal/api/v1/media - fetching stored media data")

    # Get stored data from service
    result = await service.get_stored_media_data()

    # Check for errors
    if "error" in result:
        return APIResponse[AnalyzeNewsResponse](
            success=False,
            error={
                "code": "ESG-AI-MEDIA-002",
                "message": result["error"]
            }
        )

    # Build response
    response = AnalyzeNewsResponse(
        total_collected=result.get("total_collected", 0),
        unique_articles=result.get("unique_articles", 0),
        articles=result.get("articles", []),
        statistics=result.get("statistics", {})
    )

    return APIResponse[AnalyzeNewsResponse](
        success=True,
        data=response,
    )


@router.post(
    "/analyze",
    response_model=APIResponse[AnalyzeNewsResponse],
    status_code=status.HTTP_200_OK,
    summary="뉴스 기사 ESG 분석",
    description="""
주어진 키워드로 뉴스 기사를 수집하고 분석합니다.

**처리 과정:**
1. 네이버 뉴스 API에서 뉴스 수집
2. 18개 ESG 이슈로 기사 분류
3. 감성 분석 수행
4. 통계 및 기사 목록 반환

**참고:** 환경변수에 네이버 API 자격증명이 필요합니다.
""",
)
async def analyze_news(
    request: AnalyzeNewsRequest,
    service: MediaAnalysisService = Depends(get_media_analysis_service),
) -> APIResponse[AnalyzeNewsResponse]:
    """
    Analyze news articles for ESG issues and sentiment.

    Args:
        request: Analysis request with keywords
        service: Media analysis service (injected)

    Returns:
        APIResponse with analysis results
    """
    logger.info(
        f"POST /internal/api/v1/media/analyze - "
        f"keywords={request.keywords}, max_pages={request.max_pages}"
    )

    # Call service
    result = await service.collect_and_analyze_news(
        keywords=request.keywords,
        max_pages=request.max_pages
    )

    # Check for errors
    if "error" in result:
        return APIResponse[AnalyzeNewsResponse](
            success=False,
            error={
                "code": "ESG-AI-MEDIA-001",
                "message": result["error"]
            }
        )

    # Build response
    response = AnalyzeNewsResponse(
        total_collected=result.get("total_collected", 0),
        unique_articles=result.get("unique_articles", 0),
        articles=result.get("articles", []),
        statistics=result.get("statistics", {})
    )

    return APIResponse[AnalyzeNewsResponse](
        success=True,
        data=response,
    )


@router.post(
    "/analyze-articles",
    response_model=APIResponse[AnalyzeNewsResponse],
    status_code=status.HTTP_200_OK,
    summary="수집된 기사 분석",
    description="""
사전 수집된 기사 목록에 대해 ESG 분류 및 감성 분석을 수행합니다.

이미 기사가 있고 분류만 필요한 경우 이 엔드포인트를 사용하세요.
""",
)
async def analyze_articles(
    articles: List[dict],
    service: MediaAnalysisService = Depends(get_media_analysis_service),
) -> APIResponse[AnalyzeNewsResponse]:
    """
    Analyze pre-collected articles.

    Args:
        articles: List of raw article data
        service: Media analysis service (injected)

    Returns:
        APIResponse with analysis results
    """
    logger.info(
        f"POST /internal/api/v1/media/analyze-articles - "
        f"article_count={len(articles)}"
    )

    # Call service
    result = service.analyze_articles(articles)

    # Build response
    response = AnalyzeNewsResponse(
        total_collected=result.get("total_articles", 0),
        unique_articles=result.get("total_articles", 0),
        articles=result.get("articles", []),
        statistics=result.get("statistics", {})
    )

    return APIResponse[AnalyzeNewsResponse](
        success=True,
        data=response,
    )


@router.get(
    "/issues",
    response_model=APIResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="ESG 이슈 정의 조회",
    description="18개 ESG 이슈 목록과 관련 키워드를 조회합니다.",
)
async def get_esg_issues(
    service: MediaAnalysisService = Depends(get_media_analysis_service),
) -> APIResponse[dict]:
    """
    Get ESG issue definitions.

    Returns:
        APIResponse with ESG issues and keywords
    """
    from app.services.media_analysis_service import (
        ESG_ISSUE_KEYWORDS,
        ESG_CATEGORY_MAP,
    )

    issues = []
    for issue_name, keywords in ESG_ISSUE_KEYWORDS.items():
        issues.append({
            "name": issue_name,
            "category": ESG_CATEGORY_MAP.get(issue_name, "ETC"),
            "keywords": keywords[:5],  # Return top 5 keywords
        })

    return APIResponse[dict](
        success=True,
        data={
            "issues": issues,
            "total_count": len(issues),
        },
    )


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="미디어 분석 서비스 헬스체크",
    description="미디어 분석 서비스 상태를 확인합니다.",
)
async def health_check() -> dict:
    """미디어 분석 서비스 헬스체크"""
    return {
        "status": "healthy",
        "module": "media_analysis",
    }
