"""
Voice Agent Ops - Security Module

JWT authentication, password hashing, and RBAC utilities.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from app.core.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TokenPayload(BaseModel):
    """JWT token payload structure."""

    sub: str  # User ID
    org_id: str  # Organization ID
    role: str  # User role
    exp: datetime


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    """Hash a password for storage."""
    return pwd_context.hash(password)


def create_access_token(
    user_id: str,
    org_id: str,
    role: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create a JWT access token."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)

    payload = {
        "sub": user_id,
        "org_id": org_id,
        "role": role,
        "exp": expire,
    }

    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> Optional[TokenPayload]:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
        return TokenPayload(
            sub=payload["sub"],
            org_id=payload["org_id"],
            role=payload["role"],
            exp=datetime.fromtimestamp(payload["exp"], tz=timezone.utc),
        )
    except JWTError:
        return None


# Role-based access control
class Role:
    """User role constants."""

    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    OPERATOR = "OPERATOR"
    QA = "QA"


# Permission mappings
ROLE_PERMISSIONS: dict[str, set[str]] = {
    Role.ADMIN: {
        "campaigns:read",
        "campaigns:write",
        "campaigns:delete",
        "calls:read",
        "calls:write",
        "analytics:read",
        "users:read",
        "users:write",
        "settings:read",
        "settings:write",
        "compliance:read",
        "compliance:write",
        "qa:read",
        "qa:write",
    },
    Role.MANAGER: {
        "campaigns:read",
        "campaigns:write",
        "calls:read",
        "calls:write",
        "analytics:read",
        "compliance:read",
        "compliance:write",
        "qa:read",
    },
    Role.OPERATOR: {
        "campaigns:read",
        "calls:read",
        "calls:write",
        "analytics:read",
    },
    Role.QA: {
        "calls:read",
        "qa:read",
        "qa:write",
        "analytics:read",
    },
}


def has_permission(role: str, permission: str) -> bool:
    """Check if a role has a specific permission."""
    role_perms = ROLE_PERMISSIONS.get(role, set())
    return permission in role_perms


def get_permissions(role: str) -> set[str]:
    """Get all permissions for a role."""
    return ROLE_PERMISSIONS.get(role, set())
