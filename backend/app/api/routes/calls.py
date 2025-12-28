"""
Voice Agent Ops - Calls Routes
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, or_, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.logging import get_logger
from app.db.session import get_db
from app.models import Call, CallOutcome, CallStatus, Customer, Vehicle
from app.schemas import (
    CallDetail,
    CallFilterParams,
    CallListItem,
    CallResolveRequest,
    MessageResponse,
    PaginatedResponse,
)
from app.api.deps import AuthenticatedUser

logger = get_logger(__name__)
router = APIRouter(prefix="/calls", tags=["Calls"])


@router.get("", response_model=PaginatedResponse[CallListItem])
async def list_calls(
    current_user: AuthenticatedUser,
    db: AsyncSession = Depends(get_db),
    branch_id: Optional[UUID] = Query(None),
    campaign_id: Optional[UUID] = Query(None),
    status_filter: Optional[CallStatus] = Query(None, alias="status"),
    outcome: Optional[CallOutcome] = Query(None),
    requires_review: Optional[bool] = Query(None),
    q: Optional[str] = Query(None, description="Search query"),
    from_date: Optional[datetime] = Query(None, alias="from"),
    to_date: Optional[datetime] = Query(None, alias="to"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> PaginatedResponse[CallListItem]:
    """
    List calls with filtering and pagination.
    """
    # Build query
    query = (
        select(Call, Customer, Vehicle)
        .join(Customer, Call.customer_id == Customer.id)
        .outerjoin(Vehicle, Call.vehicle_id == Vehicle.id)
        .where(Call.org_id == current_user.org_id)
    )

    # Apply filters
    if branch_id:
        query = query.where(Call.branch_id == branch_id)
    if campaign_id:
        query = query.where(Call.campaign_id == campaign_id)
    if status_filter:
        query = query.where(Call.status == status_filter)
    if outcome:
        query = query.where(Call.outcome == outcome)
    if requires_review is not None:
        query = query.where(Call.requires_human_review == requires_review)
    if from_date:
        query = query.where(Call.started_at >= from_date)
    if to_date:
        query = query.where(Call.started_at <= to_date)
    if q:
        search_term = f"%{q}%"
        query = query.where(
            or_(
                Customer.first_name.ilike(search_term),
                Customer.last_name.ilike(search_term),
                Customer.phone_e164.ilike(search_term),
                Vehicle.plate_number.ilike(search_term),
            )
        )

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Pagination
    offset = (page - 1) * page_size
    query = query.order_by(Call.started_at.desc()).offset(offset).limit(page_size)

    result = await db.execute(query)
    rows = result.all()

    items = [
        CallListItem(
            id=call.id,
            customer_name=f"{customer.first_name} {customer.last_name}",
            customer_phone=customer.phone_e164,
            vehicle_display=vehicle.display_name if vehicle else None,
            plate_number=vehicle.plate_number if vehicle else None,
            direction=call.direction,
            status=call.status,
            outcome=call.outcome,
            started_at=call.started_at,
            duration_sec=call.duration_sec,
            sentiment_label=call.sentiment_label,
            requires_human_review=call.requires_human_review,
        )
        for call, customer, vehicle in rows
    ]

    pages = (total + page_size - 1) // page_size

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.get("/{call_id}", response_model=CallDetail)
async def get_call(
    call_id: UUID,
    current_user: AuthenticatedUser,
    db: AsyncSession = Depends(get_db),
) -> CallDetail:
    """
    Get detailed call information for drawer view.
    """
    result = await db.execute(
        select(Call, Customer, Vehicle)
        .join(Customer, Call.customer_id == Customer.id)
        .outerjoin(Vehicle, Call.vehicle_id == Vehicle.id)
        .where(
            Call.id == call_id,
            Call.org_id == current_user.org_id,
        )
    )
    row = result.first()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Call not found",
        )

    call, customer, vehicle = row

    return CallDetail(
        id=call.id,
        org_id=call.org_id,
        branch_id=call.branch_id,
        campaign_id=call.campaign_id,
        customer_id=call.customer_id,
        vehicle_id=call.vehicle_id,
        job_id=call.job_id,
        customer_name=f"{customer.first_name} {customer.last_name}",
        customer_phone=customer.phone_e164,
        vehicle_display=vehicle.display_name if vehicle else None,
        plate_number=vehicle.plate_number if vehicle else None,
        direction=call.direction,
        status=call.status,
        outcome=call.outcome,
        started_at=call.started_at,
        ended_at=call.ended_at,
        duration_sec=call.duration_sec,
        eleven_conversation_id=call.eleven_conversation_id,
        eleven_call_id=call.eleven_call_id,
        recording_url=call.recording_url,
        transcript_text=call.transcript_text,
        summary_text=call.summary_text,
        extracted_fields_json=call.extracted_fields_json,
        confidence_json=call.confidence_json,
        sentiment_label=call.sentiment_label,
        sentiment_score=call.sentiment_score,
        disclosure_spoken=call.disclosure_spoken,
        requires_human_review=call.requires_human_review,
        human_assigned_to=call.human_assigned_to,
        resolution_notes=call.resolution_notes,
        created_at=call.created_at,
        updated_at=call.updated_at,
    )


@router.post("/{call_id}/resolve", response_model=MessageResponse)
async def resolve_call(
    call_id: UUID,
    request: CallResolveRequest,
    current_user: AuthenticatedUser,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """
    Resolve or take action on a call.
    
    Actions:
    - assign_human: Assign to a human agent
    - add_note: Add resolution notes
    - mark_resolved: Mark as resolved
    """
    result = await db.execute(
        select(Call).where(
            Call.id == call_id,
            Call.org_id == current_user.org_id,
        )
    )
    call = result.scalar_one_or_none()

    if not call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Call not found",
        )

    if request.action == "assign_human":
        if not request.assign_to_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="assign_to_user_id required for assign_human action",
            )
        call.human_assigned_to = request.assign_to_user_id
        call.requires_human_review = True
        message = "Call assigned to human agent"

    elif request.action == "add_note":
        if not request.notes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="notes required for add_note action",
            )
        call.resolution_notes = request.notes
        message = "Notes added to call"

    elif request.action == "mark_resolved":
        call.requires_human_review = False
        if request.notes:
            call.resolution_notes = request.notes
        message = "Call marked as resolved"

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown action: {request.action}",
        )

    await db.commit()
    logger.info(f"Call {call_id} resolved: {request.action} by {current_user.email}")

    return MessageResponse(message=message)
