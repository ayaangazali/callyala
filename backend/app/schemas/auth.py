"""
Voice Agent Ops - Auth Schemas
"""

from uuid import UUID

from pydantic import EmailStr, Field

from app.models.enums import UserRole
from app.schemas.base import BaseSchema, IDMixin, TimestampMixin


class LoginRequest(BaseSchema):
    """Login request payload."""

    email: EmailStr
    password: str = Field(min_length=8)


class TokenResponse(BaseSchema):
    """JWT token response."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class UserBase(BaseSchema):
    """Base user fields."""

    email: EmailStr
    name: str = Field(min_length=1, max_length=255)
    role: UserRole = UserRole.OPERATOR


class UserCreate(UserBase):
    """Create user request."""

    password: str = Field(min_length=8)
    org_id: UUID


class UserUpdate(BaseSchema):
    """Update user request."""

    name: str | None = None
    role: UserRole | None = None
    is_active: bool | None = None


class UserResponse(UserBase, IDMixin, TimestampMixin):
    """User response."""

    org_id: UUID
    is_active: bool


class CurrentUser(BaseSchema):
    """Current authenticated user context."""

    id: UUID
    org_id: UUID
    email: str
    name: str
    role: UserRole
