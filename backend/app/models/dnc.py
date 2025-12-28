"""
Voice Agent Ops - DNC (Do Not Call) Entry Model
"""

import uuid
from typing import Optional

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDMixin


class DncEntry(Base, UUIDMixin, TimestampMixin):
    """Do Not Call list entry for compliance."""

    __tablename__ = "dnc_entries"

    __table_args__ = (
        UniqueConstraint("org_id", "phone_e164", name="uq_dnc_entries_org_phone"),
    )

    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("orgs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    phone_e164: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source: Mapped[str] = mapped_column(String(50), default="MANUAL", nullable=False)
