"""
Voice Agent Ops - Enum Types

Database enum types for consistent values across models.
"""

import enum


class UserRole(str, enum.Enum):
    """User role types."""

    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    OPERATOR = "OPERATOR"
    QA = "QA"


class Language(str, enum.Enum):
    """Supported languages."""

    EN = "EN"
    AR = "AR"


class JobStatus(str, enum.Enum):
    """Service job status."""

    READY_FOR_PICKUP = "READY_FOR_PICKUP"
    CLOSED = "CLOSED"


class ScriptPurpose(str, enum.Enum):
    """Script purpose types."""

    READY_FOR_PICKUP = "READY_FOR_PICKUP"
    SERVICE_REMINDER = "SERVICE_REMINDER"
    FOLLOW_UP = "FOLLOW_UP"


class CampaignStatus(str, enum.Enum):
    """Campaign lifecycle status."""

    DRAFT = "DRAFT"
    READY = "READY"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class TargetStatus(str, enum.Enum):
    """Campaign target status."""

    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"
    FAILED = "FAILED"
    OPTED_OUT = "OPTED_OUT"


class CallDirection(str, enum.Enum):
    """Call direction."""

    OUTBOUND = "OUTBOUND"
    INBOUND = "INBOUND"


class CallStatus(str, enum.Enum):
    """Call lifecycle status."""

    QUEUED = "QUEUED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class CallOutcome(str, enum.Enum):
    """Call outcome types."""

    BOOKED = "BOOKED"
    NO_ANSWER = "NO_ANSWER"
    VOICEMAIL = "VOICEMAIL"
    BUSY = "BUSY"
    WRONG_NUMBER = "WRONG_NUMBER"
    OPT_OUT = "OPT_OUT"
    CALLBACK_REQUESTED = "CALLBACK_REQUESTED"
    RESCHEDULED = "RESCHEDULED"
    OTHER = "OTHER"


class SentimentLabel(str, enum.Enum):
    """Sentiment classification."""

    POS = "POS"
    NEU = "NEU"
    NEG = "NEG"


class AppointmentType(str, enum.Enum):
    """Appointment type."""

    PICKUP = "PICKUP"
    SERVICE = "SERVICE"


class AppointmentStatus(str, enum.Enum):
    """Appointment status."""

    BOOKED = "BOOKED"
    RESCHEDULED = "RESCHEDULED"
    CANCELED = "CANCELED"
    COMPLETED = "COMPLETED"


class AppointmentSource(str, enum.Enum):
    """Appointment booking source."""

    AI = "AI"
    HUMAN = "HUMAN"
