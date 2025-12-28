"""
Voice Agent Ops - Campaign Schemas
"""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import Field

from app.models.enums import CampaignStatus, ScriptPurpose, TargetStatus
from app.schemas.base import BaseSchema, IDMixin, TimestampMixin


class ScheduleWindow(BaseSchema):
    """Campaign schedule window configuration."""

    days: list[str] = Field(default=["MON", "TUE", "WED", "THU", "FRI"])
    start_hour: int = Field(default=9, ge=0, le=23)
    end_hour: int = Field(default=17, ge=0, le=23)
    timezone: str = "America/New_York"


class RetryPolicy(BaseSchema):
    """Campaign retry policy configuration."""

    max_attempts: int = Field(default=3, ge=1, le=10)
    retry_delay_hours: int = Field(default=4, ge=1)
    retry_on_no_answer: bool = True
    retry_on_busy: bool = True
    retry_on_voicemail: bool = False


class VoiceConfig(BaseSchema):
    """Voice agent configuration."""

    voice_id: str | None = None
    language: str = "en"
    speed: float = Field(default=1.0, ge=0.5, le=2.0)


class CampaignBase(BaseSchema):
    """Base campaign fields."""

    name: str = Field(min_length=1, max_length=255)
    purpose: ScriptPurpose = ScriptPurpose.READY_FOR_PICKUP


class CampaignCreate(CampaignBase):
    """Create campaign request."""

    branch_id: UUID
    script_id: UUID | None = None
    schedule_window: ScheduleWindow | None = None
    retry_policy: RetryPolicy | None = None
    voice_config: VoiceConfig | None = None


class CampaignUpdate(BaseSchema):
    """Update campaign request."""

    name: str | None = None
    script_id: UUID | None = None
    schedule_window: ScheduleWindow | None = None
    retry_policy: RetryPolicy | None = None
    voice_config: VoiceConfig | None = None


class CampaignResponse(CampaignBase, IDMixin, TimestampMixin):
    """Campaign response."""

    org_id: UUID
    branch_id: UUID
    script_id: UUID | None
    status: CampaignStatus
    schedule_window_json: dict[str, Any] | None
    retry_policy_json: dict[str, Any] | None
    voice_config_json: dict[str, Any] | None
    eleven_batch_id: str | None

    # Computed stats
    total_targets: int = 0
    pending_targets: int = 0
    completed_targets: int = 0
    booked_count: int = 0


class CampaignListItem(BaseSchema, IDMixin):
    """Campaign list item."""

    name: str
    purpose: ScriptPurpose
    status: CampaignStatus
    branch_id: UUID
    created_at: datetime
    total_targets: int = 0
    completed_targets: int = 0
    booked_count: int = 0


# Target schemas
class TargetCreateItem(BaseSchema):
    """Single target in upload request."""

    phone: str = Field(description="Phone number in E.164 format")
    first_name: str
    last_name: str
    plate_number: str | None = None
    vehicle_make: str | None = None
    vehicle_model: str | None = None
    job_id: UUID | None = None


class TargetUploadRequest(BaseSchema):
    """Upload targets request (JSON array)."""

    targets: list[TargetCreateItem]


class TargetResponse(BaseSchema, IDMixin, TimestampMixin):
    """Campaign target response."""

    campaign_id: UUID
    customer_id: UUID
    vehicle_id: UUID | None
    job_id: UUID | None
    status: TargetStatus
    attempts_count: int
    last_attempt_at: datetime | None
    next_attempt_at: datetime | None
    last_outcome: str | None


class TargetUploadResult(BaseSchema):
    """Result of target upload operation."""

    total_received: int
    created: int
    skipped_dnc: int
    skipped_duplicate: int
    errors: list[str]
