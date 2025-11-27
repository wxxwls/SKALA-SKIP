"""Benchmark Analysis Pydantic schemas."""
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class CompanyPDF(BaseModel):
    """Company PDF document info."""
    id: str = Field(..., description="Document ID")
    name: str = Field(..., description="File name")
    company_name: str = Field(..., description="Company name extracted from filename")
    size: int = Field(..., description="File size in bytes")
    uploaded_at: str = Field(..., description="Upload timestamp")
    status: str = Field(default="pending", description="Processing status")


class BenchmarkUploadResponse(BaseModel):
    """Response for benchmark PDF upload."""
    success: bool = Field(default=True)
    documents: List[CompanyPDF] = Field(default_factory=list)
    count: int = Field(default=0)
    message: Optional[str] = None


class BenchmarkPDFListResponse(BaseModel):
    """Response for listing benchmark PDFs."""
    success: bool = Field(default=True)
    documents: List[CompanyPDF] = Field(default_factory=list)
    count: int = Field(default=0)


class KeywordAnalysisResult(BaseModel):
    """Keyword analysis result for a company."""
    company_name: str = Field(..., description="Company name")
    keywords: Dict[str, int] = Field(default_factory=dict, description="Keyword frequency map")
    top_issues: List[str] = Field(default_factory=list, description="Top ESG issues")
    esg_scores: Dict[str, float] = Field(default_factory=dict, description="E/S/G category scores")


class BenchmarkAnalyzeRequest(BaseModel):
    """Request for benchmark analysis."""
    company_id: str = Field(..., description="Target company ID")
    document_ids: List[str] = Field(default_factory=list, description="Document IDs to analyze")
    analysis_type: str = Field(default="keyword", description="Analysis type")


class BenchmarkAnalyzeResponse(BaseModel):
    """Response for benchmark analysis."""
    success: bool = Field(default=True)
    company_id: str = Field(..., description="Target company ID")
    results: List[KeywordAnalysisResult] = Field(default_factory=list)
    summary: Optional[str] = None
    message: Optional[str] = None
