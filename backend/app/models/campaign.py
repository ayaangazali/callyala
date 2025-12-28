"""
Voice Agent Ops - Campaign Model
"""

import uuid
from typing import TYPE_CHECKING, Any, List, Optional

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin
from app.models.enums import CampaignStatus, ScriptPurpose

if TYPE_CHECKING:
    from app.models.campaign_target import CampaignTarget


class Campaign(Base, UUIDMixin, TimestampMixin):
    """Outbound calling campaign."""

    __tablename__ = "campaigns"

    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("orgs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    branch_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("branches.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    purpose: Mapped[ScriptPurpose] = mapped_column(
        Enum(ScriptPurpose, name="campaign_purpose"),
        default=ScriptPurpose.READY_FOR_PICKUP,
        nullable=False,
    )
    script_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("scripts.id", ondelete="SET NULL"),
        nullable=True,
    )
    status: Mapped[CampaignStatus] = mapped_column(
        Enum(CampaignStatus, name="campaign_status"),
        default=CampaignStatus.DRAFT,
        nullable=False,
        index=True,
    )
    schedule_window_json: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    retry_policy_json: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    voice_config_json: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    eleven_batch_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationships
    targets: Mapped[List["CampaignTarget"]] = relationship(
        "CampaignTarget", back_populates="campaign", cascade="all, delete-orphan"
    )
