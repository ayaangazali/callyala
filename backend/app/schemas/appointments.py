"""
Voice Agent Ops - Appointment Schemas
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import Field

from app.models.enums import AppointmentStatus
from app.schemas.base import BaseSchema, IDMixin, TimestampMixin


class AppointmentBase(BaseSchema):
    """Base appointment fields."""

    scheduled_at: datetime
    estimated_duration_minutes: Optional[int] = None
    notes: Optional[str] = None


class AppointmentCreate(AppointmentBase):
    """Create appointment request."""

    customer_id: UUID
    vehicle_id: Optional[UUID] = None
    job_id: Optional[UUID] = None
    branch_id: Optional[UUID] = None
    source: Optional[str] = None


class AppointmentUpdate(BaseSchema):
    """Update appointment request."""

    scheduled_at: Optional[datetime] = None
    estimated_duration_minutes: Optional[int] = None
    status: Optional[AppointmentStatus] = None
    notes: Optional[str] = None
    cancellation_reason: Optional[str] = None


class AppointmentResponse(AppointmentBase, IDMixin, TimestampMixin):
    """Appointment response."""

    customer_id: UUID
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    vehicle_id: Optional[UUID] = None
    vehicle_description: Optional[str] = None
    branch_id: Optional[UUID] = None
    branch_name: Optional[str] = None
    job_id: Optional[UUID] = None
    job_name: Optional[str] = None
    call_id: Optional[UUID] = None
    status: AppointmentStatus
    source: str
    reminder_sent: bool
    confirmed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    cancellation_reason: Optional[str] = None


class AppointmentListResponse(BaseSchema):
    """Paginated appointment list response."""

    items: list[AppointmentResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
