"""
Voice Agent Ops - Script Schemas
"""

from typing import Any, Optional
from uuid import UUID
from datetime import datetime

from pydantic import Field

from app.schemas.base import BaseSchema, IDMixin, TimestampMixin


class ScriptBase(BaseSchema):
    """Base script fields."""

    name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    voice_id: str
    first_message: str
    system_prompt: str
    model_id: str = "gpt-4o-mini"
    temperature: float = 0.7
    max_duration_seconds: int = 300
    language: str = "en"
    variables: list[dict[str, Any]] = []


class ScriptCreate(ScriptBase):
    """Create script request."""
    pass


class ScriptUpdate(BaseSchema):
    """Update script request."""

    name: Optional[str] = None
    description: Optional[str] = None
    voice_id: Optional[str] = None
    first_message: Optional[str] = None
    system_prompt: Optional[str] = None
    model_id: Optional[str] = None
    temperature: Optional[float] = None
    max_duration_seconds: Optional[int] = None
    language: Optional[str] = None
    variables: Optional[list[dict[str, Any]]] = None
    is_active: Optional[bool] = None


class ScriptResponse(ScriptBase, IDMixin, TimestampMixin):
    """Script response."""

    is_active: bool
    version: int
    created_by_id: Optional[UUID] = None


class ScriptListResponse(BaseSchema):
    """Paginated script list response."""

    items: list[ScriptResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
