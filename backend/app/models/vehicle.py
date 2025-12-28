"""
Voice Agent Ops - Vehicle Model
"""

import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.customer import Customer


class Vehicle(Base, UUIDMixin, TimestampMixin):
    """Customer vehicle."""

    __tablename__ = "vehicles"

    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("orgs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    make: Mapped[str] = mapped_column(String(100), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    plate_number: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    vin: Mapped[Optional[str]] = mapped_column(String(17), nullable=True)
    year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    color: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Relationships
    customer: Mapped["Customer"] = relationship("Customer", back_populates="vehicles")

    @property
    def display_name(self) -> str:
        """Get vehicle display string."""
        year_str = f"{self.year} " if self.year else ""
        return f"{year_str}{self.make} {self.model}"
