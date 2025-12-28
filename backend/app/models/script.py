"""
Voice Agent Ops - Script Model (Call Scripts/Prompts)
"""

import uuid
from typing import Any, Optional

from sqlalchemy import Boolean, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDMixin
from app.models.enums import Language, ScriptPurpose


class Script(Base, UUIDMixin, TimestampMixin):
    """AI voice agent script/prompt template."""

    __tablename__ = "scripts"

    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("orgs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    purpose: Mapped[ScriptPurpose] = mapped_column(
        Enum(ScriptPurpose, name="script_purpose"),
        default=ScriptPurpose.READY_FOR_PICKUP,
        nullable=False,
    )
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    language: Mapped[Language] = mapped_column(
        Enum(Language, name="script_language"), default=Language.EN, nullable=False
    )
    content_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    requires_disclosure: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
