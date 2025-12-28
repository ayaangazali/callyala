"""
Voice Agent Ops - SQLAlchemy Models

All models exported for easy importing.
"""

from app.models.appointment import Appointment
from app.models.audit_log import AuditLog
from app.models.branch import Branch
from app.models.call import Call
from app.models.campaign import Campaign
from app.models.campaign_target import CampaignTarget
from app.models.customer import Customer
from app.models.dnc import DncEntry
from app.models.enums import (
    AppointmentSource,
    AppointmentStatus,
    AppointmentType,
    CallDirection,
    CallOutcome,
    CallStatus,
    CampaignStatus,
    JobStatus,
    Language,
    ScriptPurpose,
    SentimentLabel,
    TargetStatus,
    UserRole,
)
from app.models.job import Job
from app.models.org import Org
from app.models.qa_review import QaReview
from app.models.script import Script
from app.models.user import User
from app.models.vehicle import Vehicle

__all__ = [
    # Models
    "Org",
    "Branch",
    "User",
    "Customer",
    "Vehicle",
    "Job",
    "Script",
    "Campaign",
    "CampaignTarget",
    "Call",
    "Appointment",
    "DncEntry",
    "QaReview",
    "AuditLog",
    # Enums
    "UserRole",
    "Language",
    "JobStatus",
    "ScriptPurpose",
    "CampaignStatus",
    "TargetStatus",
    "CallDirection",
    "CallOutcome",
    "CallStatus",
    "SentimentLabel",
    "AppointmentType",
    "AppointmentStatus",
    "AppointmentSource",
]
