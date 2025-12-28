"""Scripts API routes."""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_permission
from app.db.session import get_db
from app.models import Script, User
from app.schemas.scripts import (
    ScriptCreate,
    ScriptUpdate,
    ScriptResponse,
    ScriptListResponse,
)

router = APIRouter(prefix="/scripts", tags=["scripts"])


@router.get("", response_model=ScriptListResponse)
async def list_scripts(
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_permission("scripts:read")),
    db: AsyncSession = Depends(get_db),
):
    """List scripts with filtering."""
    query = select(Script).where(Script.org_id == current_user.org_id)

    # Apply filters
    if is_active is not None:
        query = query.where(Script.is_active == is_active)
    if search:
        query = query.where(Script.name.ilike(f"%{search}%"))

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query) or 0

    # Apply pagination and ordering
    query = (
        query.order_by(Script.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    result = await db.execute(query)
    scripts = result.scalars().all()

    return ScriptListResponse(
        items=[
            ScriptResponse(
                id=script.id,
                name=script.name,
                description=script.description,
                voice_id=script.voice_id,
                first_message=script.first_message,
                system_prompt=script.system_prompt,
                model_id=script.model_id,
                temperature=float(script.temperature),
                max_duration_seconds=script.max_duration_seconds,
                language=script.language,
                variables=script.variables,
                is_active=script.is_active,
                version=script.version,
                created_by_id=script.created_by_id,
                created_at=script.created_at,
                updated_at=script.updated_at,
            )
            for script in scripts
        ],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.post("", response_model=ScriptResponse, status_code=status.HTTP_201_CREATED)
async def create_script(
    data: ScriptCreate,
    current_user: User = Depends(require_permission("scripts:write")),
    db: AsyncSession = Depends(get_db),
):
    """Create a new script."""
    script = Script(
        org_id=current_user.org_id,
        name=data.name,
        description=data.description,
        voice_id=data.voice_id,
        first_message=data.first_message,
        system_prompt=data.system_prompt,
        model_id=data.model_id or "gpt-4o-mini",
        temperature=data.temperature or 0.7,
        max_duration_seconds=data.max_duration_seconds or 300,
        language=data.language or "en",
        variables=data.variables or [],
        is_active=True,
        version=1,
        created_by_id=current_user.id,
    )
    db.add(script)
    await db.commit()
    await db.refresh(script)

    return ScriptResponse(
        id=script.id,
        name=script.name,
        description=script.description,
        voice_id=script.voice_id,
        first_message=script.first_message,
        system_prompt=script.system_prompt,
        model_id=script.model_id,
        temperature=float(script.temperature),
        max_duration_seconds=script.max_duration_seconds,
        language=script.language,
        variables=script.variables,
        is_active=script.is_active,
        version=script.version,
        created_by_id=script.created_by_id,
        created_at=script.created_at,
        updated_at=script.updated_at,
    )


@router.get("/{script_id}", response_model=ScriptResponse)
async def get_script(
    script_id: UUID,
    current_user: User = Depends(require_permission("scripts:read")),
    db: AsyncSession = Depends(get_db),
):
    """Get script details."""
    script = await db.get(Script, script_id)
    if not script or script.org_id != current_user.org_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Script not found",
        )

    return ScriptResponse(
        id=script.id,
        name=script.name,
        description=script.description,
        voice_id=script.voice_id,
        first_message=script.first_message,
        system_prompt=script.system_prompt,
        model_id=script.model_id,
        temperature=float(script.temperature),
        max_duration_seconds=script.max_duration_seconds,
        language=script.language,
        variables=script.variables,
        is_active=script.is_active,
        version=script.version,
        created_by_id=script.created_by_id,
        created_at=script.created_at,
        updated_at=script.updated_at,
    )


@router.patch("/{script_id}", response_model=ScriptResponse)
async def update_script(
    script_id: UUID,
    data: ScriptUpdate,
    current_user: User = Depends(require_permission("scripts:write")),
    db: AsyncSession = Depends(get_db),
):
    """Update a script. Creates a new version."""
    script = await db.get(Script, script_id)
    if not script or script.org_id != current_user.org_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Script not found",
        )

    update_data = data.model_dump(exclude_unset=True)
    
    # Check if content changed to increment version
    content_fields = ["voice_id", "first_message", "system_prompt", "model_id", "temperature"]
    content_changed = any(
        field in update_data and getattr(script, field) != update_data[field]
        for field in content_fields
    )
    
    if content_changed:
        script.version += 1

    for key, value in update_data.items():
        setattr(script, key, value)

    await db.commit()
    await db.refresh(script)

    return ScriptResponse(
        id=script.id,
        name=script.name,
        description=script.description,
        voice_id=script.voice_id,
        first_message=script.first_message,
        system_prompt=script.system_prompt,
        model_id=script.model_id,
        temperature=float(script.temperature),
        max_duration_seconds=script.max_duration_seconds,
        language=script.language,
        variables=script.variables,
        is_active=script.is_active,
        version=script.version,
        created_by_id=script.created_by_id,
        created_at=script.created_at,
        updated_at=script.updated_at,
    )


@router.delete("/{script_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_script(
    script_id: UUID,
    current_user: User = Depends(require_permission("scripts:write")),
    db: AsyncSession = Depends(get_db),
):
    """Delete a script (soft delete by deactivating)."""
    script = await db.get(Script, script_id)
    if not script or script.org_id != current_user.org_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Script not found",
        )

    # Soft delete
    script.is_active = False
    await db.commit()


@router.post("/{script_id}/duplicate", response_model=ScriptResponse, status_code=status.HTTP_201_CREATED)
async def duplicate_script(
    script_id: UUID,
    current_user: User = Depends(require_permission("scripts:write")),
    db: AsyncSession = Depends(get_db),
):
    """Duplicate a script."""
    script = await db.get(Script, script_id)
    if not script or script.org_id != current_user.org_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Script not found",
        )

    new_script = Script(
        org_id=current_user.org_id,
        name=f"{script.name} (Copy)",
        description=script.description,
        voice_id=script.voice_id,
        first_message=script.first_message,
        system_prompt=script.system_prompt,
        model_id=script.model_id,
        temperature=script.temperature,
        max_duration_seconds=script.max_duration_seconds,
        language=script.language,
        variables=script.variables,
        is_active=True,
        version=1,
        created_by_id=current_user.id,
    )
    db.add(new_script)
    await db.commit()
    await db.refresh(new_script)

    return ScriptResponse(
        id=new_script.id,
        name=new_script.name,
        description=new_script.description,
        voice_id=new_script.voice_id,
        first_message=new_script.first_message,
        system_prompt=new_script.system_prompt,
        model_id=new_script.model_id,
        temperature=float(new_script.temperature),
        max_duration_seconds=new_script.max_duration_seconds,
        language=new_script.language,
        variables=new_script.variables,
        is_active=new_script.is_active,
        version=new_script.version,
        created_by_id=new_script.created_by_id,
        created_at=new_script.created_at,
        updated_at=new_script.updated_at,
    )
