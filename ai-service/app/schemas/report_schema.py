"""Report Generation Pydantic schemas."""
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class KPIData(BaseModel):
    """KPI data for report generation."""
    # Support both naming conventions
    name: Optional[str] = Field(None, description="KPI name")
    kpi_name: Optional[str] = Field(None, description="KPI name (alias)")
    value: Optional[str] = Field(None, description="KPI value")
    kpi_value: Optional[str] = Field(None, description="KPI value (alias)")
    unit: Optional[str] = Field(None, description="Unit of measurement")
    year: Optional[int] = Field(None, description="Year of the data")
    target: Optional[str] = Field(None, description="Target value")
    is_null: bool = Field(default=False, description="Whether value is null")


class IssueForReport(BaseModel):
    """Issue data for report generation."""
    # Support both naming conventions (frontend uses id/name, backend uses issue_id/issue_name)
    id: Optional[str] = Field(None, description="Issue ID (alias)")
    issue_id: Optional[str] = Field(None, description="Issue ID")
    name: Optional[str] = Field(None, description="Issue name (alias)")
    issue_name: Optional[str] = Field(None, description="Issue name in Korean")
    category: str = Field(..., description="ESG category (E/S/G)")
    financial_score: float = Field(default=0.0, description="Financial materiality score")
    impact_score: float = Field(default=0.0, description="Impact materiality score")
    is_priority: bool = Field(default=False, description="Is priority issue")
    description: Optional[str] = Field(None, description="Issue description")
    kpis: List[KPIData] = Field(default_factory=list, description="Related KPIs")

    @property
    def get_issue_id(self) -> str:
        """Get issue ID from either field."""
        return self.issue_id or self.id or ""

    @property
    def get_issue_name(self) -> str:
        """Get issue name from either field."""
        return self.issue_name or self.name or ""


class CompanyContext(BaseModel):
    """Company context for report generation."""
    company_id: str = Field(..., description="Company ID")
    company_name: str = Field(..., description="Company name")
    industry: str = Field(..., description="Industry type")
    year: int = Field(..., description="Report year")


class ReportGenerationRequest(BaseModel):
    """Request for ESG report generation."""
    company_context: CompanyContext = Field(..., description="Company context")
    issues: List[IssueForReport] = Field(..., description="Issues for report")
    previous_report: Optional[str] = Field(None, description="Previous year's report text")
    # Frontend compatibility fields
    impact_priority_issue_ids: List[str] = Field(default_factory=list, description="Impact materiality top 5 issue IDs")
    financial_priority_issue_ids: List[str] = Field(default_factory=list, description="Financial materiality top 5 issue IDs")
    priority_issue_ids: List[str] = Field(default_factory=list, description="Deprecated: use impact/financial fields")
    kpi_data_by_issue: Dict[str, List[KPIData]] = Field(default_factory=dict, description="KPI data by issue ID")
    language: str = Field(default="ko", description="Report language (ko/en)")


class SectionData(BaseModel):
    """Generated section data."""
    # Required fields
    issue_id: str = Field(..., description="Issue ID")
    issue_name: str = Field(..., description="Issue name")
    category: str = Field(..., description="ESG category (E/S/G)")
    section_html: str = Field(..., description="Generated HTML content")
    # Optional fields
    section_id: Optional[str] = Field(None, description="Section ID (legacy)")
    title: Optional[str] = Field(None, description="Section title (legacy)")
    content: Optional[str] = Field(None, description="Generated HTML content (legacy)")
    materiality_type: str = Field(default="impact", description="Materiality type (impact/financial)")
    priority_rank: int = Field(default=1, description="Priority rank (1-5)")
    has_kpi_data: bool = Field(default=False, description="Whether KPI data is available")
    missing_kpis: List[str] = Field(default_factory=list, description="List of missing KPIs")


class ProcessingMetadata(BaseModel):
    """Report processing metadata."""
    total_issues: int = Field(default=0, description="Total issues processed")
    sections_generated: int = Field(default=0, description="Number of sections generated")
    processing_time_ms: int = Field(default=0, description="Processing time in milliseconds")
    model_used: str = Field(default="", description="LLM model used")
    # Additional fields used by service
    ai_model: str = Field(default="", description="AI model used (alias)")
    tokens_used: Optional[int] = Field(None, description="Tokens used")
    sources_used: List[str] = Field(default_factory=list, description="Data sources used")


class ErrorInfo(BaseModel):
    """Error information."""
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: Optional[str] = Field(None, description="Error details")


class ReportGenerationResponse(BaseModel):
    """Response for ESG report generation."""
    success: bool = Field(default=True)
    report_html: Optional[str] = Field(None, description="Generated report HTML")
    report_markdown: Optional[str] = Field(None, description="Generated report Markdown")
    sections: List[SectionData] = Field(default_factory=list, description="Individual sections")
    metadata: Optional[ProcessingMetadata] = Field(None, description="Processing metadata")
    error: Optional[ErrorInfo] = Field(None, description="Error info if failed")


class ReportModifyRequest(BaseModel):
    """Request for report modification."""
    company_name: str = Field(..., description="Company name")
    current_report: str = Field(..., description="Current report HTML")
    instruction: str = Field(..., description="Modification instruction")


class ReportModifyResponse(BaseModel):
    """Response for report modification."""
    success: bool = Field(default=True)
    modified_report: Optional[str] = Field(None, description="Modified report HTML")
    modified_html: Optional[str] = Field(None, description="Modified HTML content")
    changes_summary: Optional[str] = Field(None, description="Summary of changes made")
    message: Optional[str] = Field(None, description="Status message")
    error: Optional[ErrorInfo] = Field(None, description="Error info if failed")
