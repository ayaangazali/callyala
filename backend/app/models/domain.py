"""Domain models for Voice Agent Ops."""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator
import phonenumbers


class CampaignStatus(str, Enum):
    """Campaign status."""
    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class CallStatus(str, Enum):
    """Call status."""
    PENDING = "pending"
    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    NO_ANSWER = "no_answer"
    BUSY = "busy"


class CallOutcome(str, Enum):
    """Call outcome - what happened during the call."""
    UNKNOWN = "unknown"
    VOICEMAIL = "voicemail"
    CALLBACK_REQUESTED = "callback_requested"
    APPOINTMENT_SET = "appointment_set"
    NOT_INTERESTED = "not_interested"
    WRONG_NUMBER = "wrong_number"
    DO_NOT_CALL = "do_not_call"
    TRANSFERRED = "transferred"
    NEEDS_FOLLOWUP = "needs_followup"


class SheetRow(BaseModel):
    """A row from Google Sheets - represents a lead."""
    row_number: int
    first_name: str = ""
    last_name: str = ""
    phone: str
    email: Optional[str] = None
    vehicle_interest: Optional[str] = None
    notes: Optional[str] = None
    extra_fields: dict[str, Any] = Field(default_factory=dict)

    @field_validator("phone", mode="before")
    @classmethod
    def normalize_phone(cls, v: str) -> str:
        """Normalize phone to E.164 format."""
        if not v:
            return v
        try:
            # Try parsing as Kuwaiti number first (default region)
            parsed = phonenumbers.parse(str(v), "KW")
            if phonenumbers.is_valid_number(parsed):
                return phonenumbers.format_number(
                    parsed, phonenumbers.PhoneNumberFormat.E164
                )
        except phonenumbers.NumberParseException:
            pass
        return str(v).strip()

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()


class Call(BaseModel):
    """A single call record."""
    id: str = Field(description="Unique call ID (UUID)")
    campaign_id: str
    row_number: int
    phone: str
    customer_name: str = ""
    
    # Status tracking
    status: CallStatus = CallStatus.PENDING
    outcome: CallOutcome = CallOutcome.UNKNOWN
    
    # ElevenLabs tracking
    elevenlabs_call_id: Optional[str] = None
    elevenlabs_batch_id: Optional[str] = None
    
    # Timing
    created_at: datetime
    queued_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    
    # Results
    transcript: Optional[str] = None
    summary: Optional[str] = None
    recording_url: Optional[str] = None
    sentiment: Optional[str] = None
    
    # Metadata
    error_message: Optional[str] = None
    retry_count: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class Campaign(BaseModel):
    """A calling campaign."""
    id: str = Field(description="Unique campaign ID (UUID)")
    name: str
    description: Optional[str] = None
    
    # Status
    status: CampaignStatus = CampaignStatus.DRAFT
    
    # Source
    sheet_id: str = Field(description="Google Sheet ID")
    sheet_range: str = Field(description="Sheet range (e.g., Sheet1!A1:Z)")
    
    # Configuration
    agent_id: str = Field(description="ElevenLabs agent ID")
    phone_number_id: str = Field(description="ElevenLabs phone number ID")
    batch_size: int = Field(default=50, ge=1, le=200)
    
    # Stats
    total_leads: int = 0
    calls_made: int = 0
    calls_completed: int = 0
    calls_successful: int = 0
    
    # Timing
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Metadata
    metadata: dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

    @property
    def progress_pct(self) -> float:
        if self.total_leads == 0:
            return 0.0
        return (self.calls_completed / self.total_leads) * 100

    @property
    def success_rate(self) -> float:
        if self.calls_completed == 0:
            return 0.0
        return (self.calls_successful / self.calls_completed) * 100
