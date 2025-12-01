"""Issue Pool Pydantic schemas."""
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class CompanyContext(BaseModel):
    """Company context for issue pool generation."""
    company_id: str = Field(..., description="Company ID")
    company_name: str = Field(..., description="Company name")
    industry: str = Field(..., description="Industry type")
    year: int = Field(..., description="Report year")


class SourceAttribution(BaseModel):
    """Source attribution for generated content."""
    source_type: str = Field(..., description="Source type (standard/benchmark/internal/news)")
    source_name: str = Field(..., description="Source name")
    relevance_score: float = Field(default=0.0, ge=0.0, le=1.0)


class TopicItem(BaseModel):
    """Single topic in issue pool."""
    topic_id: str = Field(..., description="Topic ID")
    topic_title: str = Field(..., description="Topic title in Korean")
    category: str = Field(..., description="ESG category (E/S/G)")
    description: str = Field(..., description="Topic description")
    financial_score: float = Field(default=0.0, ge=0.0, le=10.0, description="Financial materiality score")
    impact_score: float = Field(default=0.0, ge=0.0, le=10.0, description="Impact materiality score")
    sources: List[SourceAttribution] = Field(default_factory=list, description="Source attributions")
    keywords: List[str] = Field(default_factory=list, description="Related keywords")


class GenerateIssuePoolRequest(BaseModel):
    """Request for issue pool generation."""
    company_context: CompanyContext = Field(..., description="Company context")
    use_standards: bool = Field(default=True, description="Use ESG standards as source")
    use_benchmarks: bool = Field(default=True, description="Use benchmark reports as source")
    use_internal: bool = Field(default=True, description="Use internal documents as source")
    use_news: bool = Field(default=True, description="Use news analysis as source")
    max_topics: int = Field(default=20, ge=1, le=50, description="Maximum topics to generate")


class IssuePoolResponse(BaseModel):
    """Response for issue pool generation."""
    company_id: str = Field(..., description="Company ID")
    year: int = Field(..., description="Report year")
    topics: List[TopicItem] = Field(default_factory=list, description="Generated topics")
    total_count: int = Field(default=0, description="Total topics generated")
    sources_used: List[str] = Field(default_factory=list, description="Sources used for generation")


class ScoreTopicRequest(BaseModel):
    """Request for topic scoring."""
    company_context: CompanyContext = Field(..., description="Company context")
    topic_title: str = Field(..., description="Topic title to score")
    topic_description: Optional[str] = Field(None, description="Topic description")


class ScoreTopicResponse(BaseModel):
    """Response for topic scoring."""
    topic_title: str = Field(..., description="Topic title")
    financial_score: float = Field(..., ge=0.0, le=10.0, description="Financial materiality score")
    impact_score: float = Field(..., ge=0.0, le=10.0, description="Impact materiality score")
    financial_rationale: str = Field(..., description="Rationale for financial score")
    impact_rationale: str = Field(..., description="Rationale for impact score")
    sources: List[SourceAttribution] = Field(default_factory=list, description="Source attributions")
