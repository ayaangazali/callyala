"""
Voice Agent Ops - Call Schemas
"""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import Field

from app.models.enums import CallDirection, CallOutcome, CallStatus, SentimentLabel
from app.schemas.base import BaseSchema, IDMixin, TimestampMixin


class CallBase(BaseSchema):
    """Base call fields."""

    direction: CallDirection = CallDirection.OUTBOUND
    status: CallStatus = CallStatus.QUEUED
    outcome: CallOutcome | None = None


class CallListItem(BaseSchema, IDMixin):
    """Call list item for table display."""

    customer_name: str
    customer_phone: str
    vehicle_display: str | None = None
    plate_number: str | None = None
    direction: CallDirection
    status: CallStatus
    outcome: CallOutcome | None
    started_at: datetime | None
    duration_sec: int | None
    sentiment_label: SentimentLabel | None
    booked_time: datetime | None = None
    requires_human_review: bool


class CallDetail(BaseSchema, IDMixin, TimestampMixin):
    """Full call detail for drawer view."""

    # Identifiers
    org_id: UUID
    branch_id: UUID
    campaign_id: UUID | None
    customer_id: UUID
    vehicle_id: UUID | None
    job_id: UUID | None

    # Customer info
    customer_name: str
    customer_phone: str

    # Vehicle info
    vehicle_display: str | None = None
    plate_number: str | None = None

    # Call metadata
    direction: CallDirection
    status: CallStatus
    outcome: CallOutcome | None
    started_at: datetime | None
    ended_at: datetime | None
    duration_sec: int | None

    # ElevenLabs IDs
    eleven_conversation_id: str | None
    eleven_call_id: str | None

    # Recording
    recording_url: str | None

    # Transcript and analysis
    transcript_text: str | None
    summary_text: str | None
    extracted_fields_json: dict[str, Any] | None
    confidence_json: dict[str, float] | None

    # Sentiment
    sentiment_label: SentimentLabel | None
    sentiment_score: float | None

    # Compliance
    disclosure_spoken: bool

    # Human review
    requires_human_review: bool
    human_assigned_to: UUID | None
    resolution_notes: str | None


class CallResolveRequest(BaseSchema):
    """Request to resolve/handle a call."""

    action: str = Field(description="Action: assign_human, add_note, mark_resolved")
    assign_to_user_id: UUID | None = None
    notes: str | None = None


class CallFilterParams(BaseSchema):
    """Call list filter parameters."""

    branch_id: UUID | None = None
    campaign_id: UUID | None = None
    status: CallStatus | None = None
    outcome: CallOutcome | None = None
    requires_review: bool | None = None
    q: str | None = Field(None, description="Search query (customer name, phone, plate)")
    from_date: datetime | None = None
    to_date: datetime | None = None
