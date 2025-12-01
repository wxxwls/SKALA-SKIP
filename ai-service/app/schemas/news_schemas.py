"""News related Pydantic schemas."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class NewsArticle(BaseModel):
    """Single news article schema."""

    id: Optional[str] = Field(None, description="Article ID")
    title: str = Field(..., description="Article title")
    content: str = Field(..., description="Article content")
    source: Optional[str] = Field(None, description="News source")
    published_at: Optional[datetime] = Field(None, description="Publication date")
    url: Optional[str] = Field(None, description="Article URL")


class SentimentResult(BaseModel):
    """Sentiment analysis result."""

    label: str = Field(..., description="Sentiment label (positive/negative/neutral)")
    score: float = Field(..., ge=0.0, le=1.0, description="Confidence score")


class TopicResult(BaseModel):
    """Topic extraction result."""

    topic: str = Field(..., description="Extracted topic")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    keywords: List[str] = Field(default_factory=list, description="Topic keywords")


class NewsAnalyzeRequest(BaseModel):
    """Request schema for news analysis."""

    articles: List[NewsArticle] = Field(..., description="Articles to analyze")
    analyze_topics: bool = Field(default=True, description="Whether to extract topics")
    analyze_sentiment: bool = Field(default=True, description="Whether to analyze sentiment")


class NewsAnalyzedArticle(BaseModel):
    """Analyzed news article with results."""

    article: NewsArticle
    sentiment: Optional[SentimentResult] = None
    topics: List[TopicResult] = Field(default_factory=list)
    esg_relevance: float = Field(default=0.0, ge=0.0, le=1.0)
    esg_category: Optional[str] = Field(None, description="Primary ESG category")


class NewsAnalyzeResponse(BaseModel):
    """Response schema for news analysis."""

    analyzed_articles: List[NewsAnalyzedArticle] = Field(default_factory=list)
    total_analyzed: int = Field(..., description="Total articles analyzed")


class NewsSentimentRequest(BaseModel):
    """Request schema for sentiment analysis."""

    texts: List[str] = Field(..., description="Texts to analyze")


class NewsSentimentResponse(BaseModel):
    """Response schema for sentiment analysis."""

    results: List[SentimentResult] = Field(default_factory=list)


class NewsCleanRequest(BaseModel):
    """Request schema for text cleaning."""

    texts: List[str] = Field(..., description="Texts to clean")
    remove_html: bool = Field(default=True)
    normalize_whitespace: bool = Field(default=True)


class NewsCleanResponse(BaseModel):
    """Response schema for text cleaning."""

    cleaned_texts: List[str] = Field(default_factory=list)
