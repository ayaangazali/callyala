"""
Voice Agent Ops - Base Schemas

Common Pydantic schemas and utilities.
"""

from datetime import datetime
from typing import Any, Generic, List, Optional, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class BaseSchema(BaseModel):
    """Base schema with common configuration."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        str_strip_whitespace=True,
    )


class TimestampMixin(BaseModel):
    """Timestamp fields for responses."""

    created_at: datetime
    updated_at: datetime


class IDMixin(BaseModel):
    """ID field for responses."""

    id: UUID


# Generic type for pagination
T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated list response."""

    items: List[T]
    total: int
    page: int = 1
    page_size: int = 20
    pages: int = 1


class MessageResponse(BaseModel):
    """Simple message response."""

    message: str
    success: bool = True


class ErrorDetail(BaseModel):
    """Error detail for validation errors."""

    loc: List[str]
    msg: str
    type: str


class ErrorResponse(BaseModel):
    """Standard error response."""

    detail: str
    errors: Optional[List[ErrorDetail]] = None


# Pagination parameters
class PaginationParams(BaseModel):
    """Common pagination parameters."""

    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


# Date range filter
class DateRangeParams(BaseModel):
    """Date range filter parameters."""

    from_date: Optional[datetime] = Field(None, alias="from")
    to_date: Optional[datetime] = Field(None, alias="to")
