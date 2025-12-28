"""
Voice Agent Ops - Customer Model
"""

import uuid
from typing import TYPE_CHECKING, Any, List, Optional

from sqlalchemy import Enum, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin
from app.models.enums import Language

if TYPE_CHECKING:
    from app.models.vehicle import Vehicle


class Customer(Base, UUIDMixin, TimestampMixin):
    """Customer contact information."""

    __tablename__ = "customers"

    __table_args__ = (
        UniqueConstraint("org_id", "phone_e164", name="uq_customers_org_phone"),
    )

    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("orgs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone_e164: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    alt_phone_e164: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    language_pref: Mapped[Language] = mapped_column(
        Enum(Language, name="language"), default=Language.EN, nullable=False
    )
    tags_json: Mapped[Optional[list[str]]] = mapped_column(JSON, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    vehicles: Mapped[List["Vehicle"]] = relationship(
        "Vehicle", back_populates="customer", cascade="all, delete-orphan"
    )

    @property
    def full_name(self) -> str:
        """Get customer's full name."""
        return f"{self.first_name} {self.last_name}"
