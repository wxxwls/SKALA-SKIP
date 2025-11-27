"""News API endpoints."""
from typing import List

from fastapi import APIRouter, Depends

from app.schemas.news_schemas import (
    NewsAnalyzeRequest,
    NewsAnalyzeResponse,
    NewsSentimentRequest,
    NewsSentimentResponse,
    NewsCleanRequest,
    NewsCleanResponse,
)
from app.services.news_service import NewsService

router = APIRouter()


def get_news_service() -> NewsService:
    """Dependency injection for NewsService."""
    return NewsService()


@router.post("/analyze", response_model=NewsAnalyzeResponse)
async def analyze_news(
    request: NewsAnalyzeRequest,
    service: NewsService = Depends(get_news_service),
) -> NewsAnalyzeResponse:
    """Analyze news articles for ESG relevance and topics."""
    return await service.analyze_news(request)


@router.post("/sentiment", response_model=NewsSentimentResponse)
async def analyze_sentiment(
    request: NewsSentimentRequest,
    service: NewsService = Depends(get_news_service),
) -> NewsSentimentResponse:
    """Analyze sentiment of news articles."""
    return await service.analyze_sentiment(request)


@router.post("/clean", response_model=NewsCleanResponse)
async def clean_news_text(
    request: NewsCleanRequest,
    service: NewsService = Depends(get_news_service),
) -> NewsCleanResponse:
    """Clean and normalize news text content."""
    return await service.clean_text(request)
