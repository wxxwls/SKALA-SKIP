"""Report related Pydantic schemas."""
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class ReportSection(BaseModel):
    """Single report section."""

    section_id: str = Field(..., description="Section identifier")
    title: str = Field(..., description="Section title")
    content: str = Field(..., description="Section content")
    order: int = Field(..., description="Section order in report")


class ReportGenerateRequest(BaseModel):
    """Request schema for report generation."""

    company_id: str = Field(..., description="Company identifier")
    report_type: str = Field(..., description="Report type (annual/quarterly/etc)")
    year: int = Field(..., description="Report year")
    sections: List[str] = Field(default_factory=list, description="Sections to generate")
    context_data: Dict[str, str] = Field(default_factory=dict, description="Additional context data")


class ReportGenerateResponse(BaseModel):
    """Response schema for report generation."""

    company_id: str = Field(..., description="Company identifier")
    report_type: str = Field(..., description="Report type")
    year: int = Field(..., description="Report year")
    sections: List[ReportSection] = Field(default_factory=list, description="Generated sections")
    total_sections: int = Field(..., description="Total number of sections")


class ReportSectionRequest(BaseModel):
    """Request schema for single section generation."""

    company_id: str = Field(..., description="Company identifier")
    section_type: str = Field(..., description="Section type to generate")
    context: Optional[str] = Field(None, description="Additional context")
    max_length: int = Field(default=1000, description="Maximum content length")


class ReportSectionResponse(BaseModel):
    """Response schema for single section generation."""

    section: ReportSection
    metadata: Dict[str, str] = Field(default_factory=dict)
