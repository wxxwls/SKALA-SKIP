"""Issue Pool related Pydantic schemas."""
from typing import List, Optional

from pydantic import BaseModel, Field


class IssueItem(BaseModel):
    """Single ESG issue item."""

    id: Optional[str] = Field(None, description="Issue ID")
    title: str = Field(..., description="Issue title")
    description: str = Field(..., description="Issue description")
    category: str = Field(..., description="ESG category (E/S/G)")
    subcategory: Optional[str] = Field(None, description="ESG subcategory")
    relevance_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Relevance score")
    keywords: List[str] = Field(default_factory=list, description="Related keywords")


class IssuePoolGenerateRequest(BaseModel):
    """Request schema for generating issue pool."""

    company_id: str = Field(..., description="Company identifier")
    industry: str = Field(..., description="Industry type")
    context: Optional[str] = Field(None, description="Additional context for generation")
    max_issues: int = Field(default=20, ge=1, le=100, description="Maximum number of issues to generate")


class IssuePoolGenerateResponse(BaseModel):
    """Response schema for generated issue pool."""

    company_id: str = Field(..., description="Company identifier")
    issues: List[IssueItem] = Field(default_factory=list, description="Generated issues")
    total_count: int = Field(..., description="Total number of generated issues")


class IssueRecommendRequest(BaseModel):
    """Request schema for issue recommendation."""

    company_id: str = Field(..., description="Company identifier")
    query: str = Field(..., description="Query text for recommendation")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of recommendations")
    category_filter: Optional[str] = Field(None, description="Filter by ESG category")


class IssueRecommendResponse(BaseModel):
    """Response schema for issue recommendations."""

    company_id: str = Field(..., description="Company identifier")
    recommendations: List[IssueItem] = Field(default_factory=list, description="Recommended issues")
    query: str = Field(..., description="Original query")
