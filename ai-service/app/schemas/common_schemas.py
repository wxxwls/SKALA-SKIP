"""Common Pydantic schemas used across the application."""
from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class HealthResponse(BaseModel):
    """Health check response schema."""

    status: str = Field(..., description="Health status (healthy/unhealthy)")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = Field(..., description="Application version")
    details: Dict[str, Any] = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    """Standard error response schema."""

    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: Dict[str, Any] = Field(default_factory=dict)


class PaginationRequest(BaseModel):
    """Pagination request parameters."""

    page: int = Field(default=1, ge=1, description="Page number")
    size: int = Field(default=20, ge=1, le=100, description="Items per page")


class PaginationResponse(BaseModel, Generic[T]):
    """Paginated response wrapper."""

    items: List[T] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page")
    size: int = Field(..., description="Items per page")
    pages: int = Field(..., description="Total number of pages")


class BaseRequest(BaseModel):
    """Base request schema with common fields."""

    request_id: Optional[str] = Field(None, description="Optional request tracking ID")


class BaseResponse(BaseModel):
    """Base response schema with common fields."""

    success: bool = Field(default=True, description="Whether the request was successful")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
