"""Appointments API routes."""
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user, require_permission
from app.db.session import get_db
from app.models import Appointment, Customer, Vehicle, Job, Branch, User
from app.models.enums import AppointmentStatus
from app.schemas.appointments import (
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentResponse,
    AppointmentListResponse,
)

router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.get("", response_model=AppointmentListResponse)
async def list_appointments(
    branch_id: Optional[UUID] = None,
    customer_id: Optional[UUID] = None,
    status: Optional[AppointmentStatus] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_permission("appointments:read")),
    db: AsyncSession = Depends(get_db),
):
    """List appointments with filtering."""
    query = select(Appointment).where(Appointment.org_id == current_user.org_id)

    # Apply filters
    if branch_id:
        query = query.where(Appointment.branch_id == branch_id)
    if customer_id:
        query = query.where(Appointment.customer_id == customer_id)
    if status:
        query = query.where(Appointment.status == status)
    if date_from:
        query = query.where(Appointment.scheduled_at >= date_from)
    if date_to:
        query = query.where(Appointment.scheduled_at <= date_to)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query) or 0

    # Apply pagination and ordering
    query = (
        query.options(
            selectinload(Appointment.customer),
            selectinload(Appointment.vehicle),
            selectinload(Appointment.job),
            selectinload(Appointment.branch),
        )
        .order_by(Appointment.scheduled_at.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    result = await db.execute(query)
    appointments = result.scalars().all()

    return AppointmentListResponse(
        items=[
            AppointmentResponse(
                id=appt.id,
                customer_id=appt.customer_id,
                customer_name=f"{appt.customer.first_name} {appt.customer.last_name}" if appt.customer else None,
                customer_phone=appt.customer.phone if appt.customer else None,
                vehicle_id=appt.vehicle_id,
                vehicle_description=(
                    f"{appt.vehicle.year} {appt.vehicle.make} {appt.vehicle.model}"
                    if appt.vehicle
                    else None
                ),
                branch_id=appt.branch_id,
                branch_name=appt.branch.name if appt.branch else None,
                job_id=appt.job_id,
                job_name=appt.job.name if appt.job else None,
                call_id=appt.call_id,
                scheduled_at=appt.scheduled_at,
                estimated_duration_minutes=appt.estimated_duration_minutes,
                status=appt.status,
                source=appt.source,
                notes=appt.notes,
                reminder_sent=appt.reminder_sent,
                confirmed_at=appt.confirmed_at,
                cancelled_at=appt.cancelled_at,
                cancellation_reason=appt.cancellation_reason,
                created_at=appt.created_at,
            )
            for appt in appointments
        ],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.post("", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def create_appointment(
    data: AppointmentCreate,
    current_user: User = Depends(require_permission("appointments:write")),
    db: AsyncSession = Depends(get_db),
):
    """Create a new appointment."""
    # Verify customer exists and belongs to org
    customer = await db.get(Customer, data.customer_id)
    if not customer or customer.org_id != current_user.org_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )

    # Verify vehicle if provided
    if data.vehicle_id:
        vehicle = await db.get(Vehicle, data.vehicle_id)
        if not vehicle or vehicle.customer_id != data.customer_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle not found or does not belong to customer",
            )

    # Verify job if provided
    if data.job_id:
        job = await db.get(Job, data.job_id)
        if not job or job.org_id != current_user.org_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found",
            )

    appointment = Appointment(
        org_id=current_user.org_id,
        branch_id=data.branch_id or current_user.branch_id,
        customer_id=data.customer_id,
        vehicle_id=data.vehicle_id,
        job_id=data.job_id,
        scheduled_at=data.scheduled_at,
        estimated_duration_minutes=data.estimated_duration_minutes,
        status=AppointmentStatus.scheduled,
        source=data.source or "manual",
        notes=data.notes,
    )
    db.add(appointment)
    await db.commit()
    await db.refresh(appointment)

    return AppointmentResponse(
        id=appointment.id,
        customer_id=appointment.customer_id,
        customer_name=f"{customer.first_name} {customer.last_name}",
        customer_phone=customer.phone,
        vehicle_id=appointment.vehicle_id,
        branch_id=appointment.branch_id,
        job_id=appointment.job_id,
        scheduled_at=appointment.scheduled_at,
        estimated_duration_minutes=appointment.estimated_duration_minutes,
        status=appointment.status,
        source=appointment.source,
        notes=appointment.notes,
        reminder_sent=appointment.reminder_sent,
        created_at=appointment.created_at,
    )


@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(
    appointment_id: UUID,
    current_user: User = Depends(require_permission("appointments:read")),
    db: AsyncSession = Depends(get_db),
):
    """Get appointment details."""
    query = (
        select(Appointment)
        .options(
            selectinload(Appointment.customer),
            selectinload(Appointment.vehicle),
            selectinload(Appointment.job),
            selectinload(Appointment.branch),
        )
        .where(
            and_(
                Appointment.id == appointment_id,
                Appointment.org_id == current_user.org_id,
            )
        )
    )
    result = await db.execute(query)
    appt = result.scalar_one_or_none()

    if not appt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found",
        )

    return AppointmentResponse(
        id=appt.id,
        customer_id=appt.customer_id,
        customer_name=f"{appt.customer.first_name} {appt.customer.last_name}" if appt.customer else None,
        customer_phone=appt.customer.phone if appt.customer else None,
        vehicle_id=appt.vehicle_id,
        vehicle_description=(
            f"{appt.vehicle.year} {appt.vehicle.make} {appt.vehicle.model}"
            if appt.vehicle
            else None
        ),
        branch_id=appt.branch_id,
        branch_name=appt.branch.name if appt.branch else None,
        job_id=appt.job_id,
        job_name=appt.job.name if appt.job else None,
        call_id=appt.call_id,
        scheduled_at=appt.scheduled_at,
        estimated_duration_minutes=appt.estimated_duration_minutes,
        status=appt.status,
        source=appt.source,
        notes=appt.notes,
        reminder_sent=appt.reminder_sent,
        confirmed_at=appt.confirmed_at,
        cancelled_at=appt.cancelled_at,
        cancellation_reason=appt.cancellation_reason,
        created_at=appt.created_at,
    )


@router.patch("/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment(
    appointment_id: UUID,
    data: AppointmentUpdate,
    current_user: User = Depends(require_permission("appointments:write")),
    db: AsyncSession = Depends(get_db),
):
    """Update an appointment."""
    appt = await db.get(Appointment, appointment_id)
    if not appt or appt.org_id != current_user.org_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found",
        )

    update_data = data.model_dump(exclude_unset=True)
    
    # Handle status transitions
    if "status" in update_data:
        new_status = update_data["status"]
        if new_status == AppointmentStatus.confirmed:
            appt.confirmed_at = datetime.now(timezone.utc)
        elif new_status == AppointmentStatus.cancelled:
            appt.cancelled_at = datetime.now(timezone.utc)
            if "cancellation_reason" in update_data:
                appt.cancellation_reason = update_data.pop("cancellation_reason")

    for key, value in update_data.items():
        setattr(appt, key, value)

    await db.commit()
    await db.refresh(appt)

    # Reload with relationships
    query = (
        select(Appointment)
        .options(
            selectinload(Appointment.customer),
            selectinload(Appointment.vehicle),
            selectinload(Appointment.job),
            selectinload(Appointment.branch),
        )
        .where(Appointment.id == appointment_id)
    )
    result = await db.execute(query)
    appt = result.scalar_one()

    return AppointmentResponse(
        id=appt.id,
        customer_id=appt.customer_id,
        customer_name=f"{appt.customer.first_name} {appt.customer.last_name}" if appt.customer else None,
        customer_phone=appt.customer.phone if appt.customer else None,
        vehicle_id=appt.vehicle_id,
        vehicle_description=(
            f"{appt.vehicle.year} {appt.vehicle.make} {appt.vehicle.model}"
            if appt.vehicle
            else None
        ),
        branch_id=appt.branch_id,
        branch_name=appt.branch.name if appt.branch else None,
        job_id=appt.job_id,
        job_name=appt.job.name if appt.job else None,
        call_id=appt.call_id,
        scheduled_at=appt.scheduled_at,
        estimated_duration_minutes=appt.estimated_duration_minutes,
        status=appt.status,
        source=appt.source,
        notes=appt.notes,
        reminder_sent=appt.reminder_sent,
        confirmed_at=appt.confirmed_at,
        cancelled_at=appt.cancelled_at,
        cancellation_reason=appt.cancellation_reason,
        created_at=appt.created_at,
    )


@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_appointment(
    appointment_id: UUID,
    current_user: User = Depends(require_permission("appointments:write")),
    db: AsyncSession = Depends(get_db),
):
    """Delete an appointment."""
    appt = await db.get(Appointment, appointment_id)
    if not appt or appt.org_id != current_user.org_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found",
        )

    await db.delete(appt)
    await db.commit()
