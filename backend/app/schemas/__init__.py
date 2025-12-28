"""
Voice Agent Ops - Pydantic Schemas

All schemas exported for easy importing.
"""

from app.schemas.analytics import (
    CallsOverTimeData,
    HourlyBucket,
    KPIStats,
    NeedsAttentionItem,
    NeedsAttentionResponse,
    OutcomeBreakdown,
    OutcomesChartData,
    OverviewResponse,
)
from app.schemas.appointments import (
    AppointmentCreate,
    AppointmentListResponse,
    AppointmentResponse,
    AppointmentUpdate,
)
from app.schemas.auth import (
    CurrentUser,
    LoginRequest,
    TokenResponse,
    UserCreate,
    UserResponse,
    UserUpdate,
)
from app.schemas.base import (
    DateRangeParams,
    ErrorResponse,
    MessageResponse,
    PaginatedResponse,
    PaginationParams,
)
from app.schemas.calls import (
    CallDetail,
    CallFilterParams,
    CallListItem,
    CallResolveRequest,
)
from app.schemas.campaigns import (
    CampaignCreate,
    CampaignListItem,
    CampaignResponse,
    CampaignUpdate,
    RetryPolicy,
    ScheduleWindow,
    TargetCreateItem,
    TargetResponse,
    TargetUploadRequest,
    TargetUploadResult,
    VoiceConfig,
)
from app.schemas.customers import (
    CustomerCreate,
    CustomerListResponse,
    CustomerResponse,
    CustomerUpdate,
    VehicleCreate,
    VehicleResponse,
)
from app.schemas.scripts import (
    ScriptCreate,
    ScriptListResponse,
    ScriptResponse,
    ScriptUpdate,
)
from app.schemas.webhooks import (
    ElevenLabsAnalysis,
    ElevenLabsPostCallPayload,
    ElevenLabsSentiment,
    WebhookVerificationError,
)

__all__ = [
    # Base
    "PaginatedResponse",
    "PaginationParams",
    "DateRangeParams",
    "MessageResponse",
    "ErrorResponse",
    # Auth
    "LoginRequest",
    "TokenResponse",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "CurrentUser",
    # Calls
    "CallListItem",
    "CallDetail",
    "CallResolveRequest",
    "CallFilterParams",
    # Campaigns
    "CampaignCreate",
    "CampaignUpdate",
    "CampaignResponse",
    "CampaignListItem",
    "ScheduleWindow",
    "RetryPolicy",
    "VoiceConfig",
    "TargetCreateItem",
    "TargetUploadRequest",
    "TargetResponse",
    "TargetUploadResult",
    # Analytics
    "KPIStats",
    "HourlyBucket",
    "CallsOverTimeData",
    "OutcomeBreakdown",
    "OutcomesChartData",
    "OverviewResponse",
    "NeedsAttentionItem",
    "NeedsAttentionResponse",
    # Appointments
    "AppointmentCreate",
    "AppointmentUpdate",
    "AppointmentResponse",
    "AppointmentListResponse",
    # Customers
    "CustomerCreate",
    "CustomerUpdate",
    "CustomerResponse",
    "CustomerListResponse",
    "VehicleCreate",
    "VehicleResponse",
    # Scripts
    "ScriptCreate",
    "ScriptUpdate",
    "ScriptResponse",
    "ScriptListResponse",
    # Webhooks
    "ElevenLabsPostCallPayload",
    "ElevenLabsAnalysis",
    "ElevenLabsSentiment",
    "WebhookVerificationError",
]
