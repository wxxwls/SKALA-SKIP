"""Common Pydantic schemas - API Response wrapper."""
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorInfo(BaseModel):
    """Error information."""
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")


class APIResponse(BaseModel, Generic[T]):
    """Standard API response wrapper."""
    success: bool = Field(default=True, description="Whether the request was successful")
    data: Optional[T] = Field(default=None, description="Response data")
    error: Optional[ErrorInfo] = Field(default=None, description="Error information if failed")
