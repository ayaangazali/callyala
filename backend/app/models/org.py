"""
Voice Agent Ops - Organization Model
"""

import uuid
from typing import TYPE_CHECKING, List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.branch import Branch
    from app.models.user import User


class Org(Base, UUIDMixin, TimestampMixin):
    """Organization (dealership group)."""

    __tablename__ = "orgs"

    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Relationships
    branches: Mapped[List["Branch"]] = relationship(
        "Branch", back_populates="org", cascade="all, delete-orphan"
    )
    users: Mapped[List["User"]] = relationship(
        "User", back_populates="org", cascade="all, delete-orphan"
    )
