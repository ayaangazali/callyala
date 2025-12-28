"""
Voice Agent Ops - Call Model
"""

import uuid
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, Integer, String, Text, Index
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDMixin
from app.models.enums import CallDirection, CallOutcome, CallStatus, SentimentLabel


class Call(Base, UUIDMixin, TimestampMixin):
    """Individual call record with transcription and analysis."""

    __tablename__ = "calls"

    __table_args__ = (
        Index("ix_calls_org_branch_started", "org_id", "branch_id", "started_at"),
    )

    # Core identifiers
    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("orgs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    branch_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("branches.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    campaign_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("campaigns.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    target_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("campaign_targets.id", ondelete="SET NULL"),
        nullable=True,
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    vehicle_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("vehicles.id", ondelete="SET NULL"),
        nullable=True,
    )
    job_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("jobs.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Call metadata
    direction: Mapped[CallDirection] = mapped_column(
        Enum(CallDirection, name="call_direction"),
        default=CallDirection.OUTBOUND,
        nullable=False,
    )
    status: Mapped[CallStatus] = mapped_column(
        Enum(CallStatus, name="call_status"),
        default=CallStatus.QUEUED,
        nullable=False,
        index=True,
    )
    outcome: Mapped[Optional[CallOutcome]] = mapped_column(
        Enum(CallOutcome, name="call_outcome"), nullable=True, index=True
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_sec: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # ElevenLabs identifiers
    eleven_conversation_id: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, unique=True, index=True
    )
    eleven_call_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    eleven_batch_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Recording
    recording_url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    recording_storage_key: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Transcript and analysis
    transcript_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    summary_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    extracted_fields_json: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    confidence_json: Mapped[Optional[dict[str, float]]] = mapped_column(JSON, nullable=True)

    # Sentiment
    sentiment_label: Mapped[Optional[SentimentLabel]] = mapped_column(
        Enum(SentimentLabel, name="sentiment_label"), nullable=True
    )
    sentiment_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Compliance
    disclosure_spoken: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Manual intervention flags
    requires_human_review: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    human_assigned_to: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    resolution_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
