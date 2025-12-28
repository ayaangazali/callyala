"""
Voice Agent Ops - Branch Model
"""

import uuid
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.org import Org


class Branch(Base, UUIDMixin, TimestampMixin):
    """Dealership branch/location."""

    __tablename__ = "branches"

    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("orgs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    timezone: Mapped[str] = mapped_column(String(50), default="America/New_York", nullable=False)
    business_hours_json: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    capacity_json: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)

    # Relationships
    org: Mapped["Org"] = relationship("Org", back_populates="branches")
