"""
Voice Agent Ops - API Dependencies

Authentication and authorization dependencies for routes.
"""

from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.core.security import Role, decode_access_token, has_permission
from app.db.session import get_db
from app.models import User
from app.schemas.auth import CurrentUser

logger = get_logger(__name__)

# Security scheme
bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> CurrentUser:
    """
    Dependency to get the current authenticated user.
    
    Validates JWT token and returns user context.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_payload = decode_access_token(credentials.credentials)
    if not token_payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user from database
    result = await db.execute(
        select(User).where(User.id == UUID(token_payload.sub))
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )

    return CurrentUser(
        id=user.id,
        org_id=user.org_id,
        email=user.email,
        name=user.name,
        role=user.role,
    )


# Type alias for current user dependency
AuthenticatedUser = Annotated[CurrentUser, Depends(get_current_user)]


def require_permission(permission: str):
    """
    Dependency factory to require a specific permission.
    
    Usage:
        @router.get("/protected", dependencies=[Depends(require_permission("campaigns:write"))])
    """
    def permission_checker(current_user: AuthenticatedUser) -> CurrentUser:
        if not has_permission(current_user.role, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {permission}",
            )
        return current_user
    return permission_checker


def require_role(*roles: str):
    """
    Dependency factory to require specific role(s).
    
    Usage:
        @router.get("/admin", dependencies=[Depends(require_role(Role.ADMIN))])
    """
    def role_checker(current_user: AuthenticatedUser) -> CurrentUser:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role required: {', '.join(roles)}",
            )
        return current_user
    return role_checker


# Common role dependencies
AdminOnly = Annotated[CurrentUser, Depends(require_role(Role.ADMIN))]
ManagerOrAdmin = Annotated[CurrentUser, Depends(require_role(Role.ADMIN, Role.MANAGER))]
QAUser = Annotated[CurrentUser, Depends(require_role(Role.ADMIN, Role.MANAGER, Role.QA))]


async def get_optional_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> CurrentUser | None:
    """
    Optional authentication - returns None if no valid token.
    Useful for endpoints that work with or without auth.
    """
    if not credentials:
        return None

    try:
        token_payload = decode_access_token(credentials.credentials)
        if not token_payload:
            return None

        result = await db.execute(
            select(User).where(User.id == UUID(token_payload.sub))
        )
        user = result.scalar_one_or_none()

        if not user or not user.is_active:
            return None

        return CurrentUser(
            id=user.id,
            org_id=user.org_id,
            email=user.email,
            name=user.name,
            role=user.role,
        )
    except Exception:
        return None


OptionalUser = Annotated[CurrentUser | None, Depends(get_optional_user)]
