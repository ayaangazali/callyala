"""
Voice Agent Ops - Webhook Schemas

Schemas for ElevenLabs post-call webhook payloads.
"""

from datetime import datetime
from typing import Any, Optional

from pydantic import Field

from app.schemas.base import BaseSchema


class ElevenLabsAnalysis(BaseSchema):
    """Analysis fields from ElevenLabs."""

    appointment_booked: bool | None = None
    pickup_date: str | None = None
    pickup_time: str | None = None
    callback_requested: bool | None = None
    callback_time: str | None = None
    opt_out: bool | None = None
    customer_confirmed: bool | None = None
    summary: str | None = None
    notes: str | None = None


class ElevenLabsSentiment(BaseSchema):
    """Sentiment analysis from ElevenLabs."""

    label: str | None = None  # positive, neutral, negative
    score: float | None = None


class ElevenLabsPostCallPayload(BaseSchema):
    """
    ElevenLabs post-call webhook payload.
    
    Note: This schema is based on expected ElevenLabs webhook format.
    Adjust field names as needed based on actual ElevenLabs documentation.
    """

    # Required identifiers
    conversation_id: str = Field(alias="conversationId")
    
    # Optional identifiers
    call_id: str | None = Field(None, alias="callId")
    batch_id: str | None = Field(None, alias="batchId")
    
    # Call metadata
    phone_number: str | None = Field(None, alias="phoneNumber")
    status: str | None = None  # completed, failed, no_answer, etc.
    started_at: datetime | None = Field(None, alias="startedAt")
    ended_at: datetime | None = Field(None, alias="endedAt")
    duration_seconds: int | None = Field(None, alias="durationSeconds")
    
    # Transcript
    transcript: str | None = None
    
    # Analysis (if ElevenLabs provides structured analysis)
    analysis: ElevenLabsAnalysis | None = None
    
    # Sentiment
    sentiment: ElevenLabsSentiment | None = None
    
    # Recording
    recording_url: str | None = Field(None, alias="recordingUrl")
    
    # Raw analysis data (for custom parsing)
    raw_analysis: dict[str, Any] | None = Field(None, alias="rawAnalysis")
    
    # Custom variables passed to the call
    metadata: dict[str, Any] | None = None


class WebhookVerificationError(BaseSchema):
    """Webhook signature verification error."""

    error: str = "Invalid webhook signature"
    detail: str | None = None
