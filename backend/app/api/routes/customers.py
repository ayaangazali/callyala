"""Customers API routes."""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user, require_permission
from app.db.session import get_db
from app.models import Customer, Vehicle, User
from app.schemas.customers import (
    CustomerCreate,
    CustomerUpdate,
    CustomerResponse,
    CustomerListResponse,
    VehicleCreate,
    VehicleResponse,
)

router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("", response_model=CustomerListResponse)
async def list_customers(
    branch_id: Optional[UUID] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_permission("customers:read")),
    db: AsyncSession = Depends(get_db),
):
    """List customers with filtering."""
    query = select(Customer).where(Customer.org_id == current_user.org_id)

    # Apply filters
    if branch_id:
        query = query.where(Customer.branch_id == branch_id)
    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                Customer.first_name.ilike(search_term),
                Customer.last_name.ilike(search_term),
                Customer.phone.ilike(search_term),
                Customer.email.ilike(search_term),
            )
        )

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query) or 0

    # Apply pagination and ordering
    query = (
        query.options(selectinload(Customer.vehicles))
        .order_by(Customer.last_name.asc(), Customer.first_name.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    result = await db.execute(query)
    customers = result.scalars().all()

    return CustomerListResponse(
        items=[
            CustomerResponse(
                id=cust.id,
                external_id=cust.external_id,
                first_name=cust.first_name,
                last_name=cust.last_name,
                phone=cust.phone,
                phone_alt=cust.phone_alt,
                email=cust.email,
                address=cust.address,
                city=cust.city,
                state=cust.state,
                zip_code=cust.zip_code,
                preferred_contact_time=cust.preferred_contact_time,
                language_preference=cust.language_preference,
                notes=cust.notes,
                branch_id=cust.branch_id,
                vehicles=[
                    VehicleResponse(
                        id=v.id,
                        vin=v.vin,
                        year=v.year,
                        make=v.make,
                        model=v.model,
                        trim=v.trim,
                        color=v.color,
                        license_plate=v.license_plate,
                        mileage=v.mileage,
                        last_service_date=v.last_service_date,
                        next_service_due=v.next_service_due,
                        is_primary=v.is_primary,
                    )
                    for v in cust.vehicles
                ],
                created_at=cust.created_at,
            )
            for cust in customers
        ],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.post("", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(
    data: CustomerCreate,
    current_user: User = Depends(require_permission("customers:write")),
    db: AsyncSession = Depends(get_db),
):
    """Create a new customer."""
    # Check for duplicate phone
    existing = await db.execute(
        select(Customer).where(
            and_(
                Customer.org_id == current_user.org_id,
                Customer.phone == data.phone,
            )
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Customer with this phone number already exists",
        )

    customer = Customer(
        org_id=current_user.org_id,
        branch_id=data.branch_id or current_user.branch_id,
        external_id=data.external_id,
        first_name=data.first_name,
        last_name=data.last_name,
        phone=data.phone,
        phone_alt=data.phone_alt,
        email=data.email,
        address=data.address,
        city=data.city,
        state=data.state,
        zip_code=data.zip_code,
        preferred_contact_time=data.preferred_contact_time,
        language_preference=data.language_preference or "en",
        notes=data.notes,
    )
    db.add(customer)
    await db.commit()
    await db.refresh(customer)

    return CustomerResponse(
        id=customer.id,
        external_id=customer.external_id,
        first_name=customer.first_name,
        last_name=customer.last_name,
        phone=customer.phone,
        phone_alt=customer.phone_alt,
        email=customer.email,
        address=customer.address,
        city=customer.city,
        state=customer.state,
        zip_code=customer.zip_code,
        preferred_contact_time=customer.preferred_contact_time,
        language_preference=customer.language_preference,
        notes=customer.notes,
        branch_id=customer.branch_id,
        vehicles=[],
        created_at=customer.created_at,
    )


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: UUID,
    current_user: User = Depends(require_permission("customers:read")),
    db: AsyncSession = Depends(get_db),
):
    """Get customer details."""
    query = (
        select(Customer)
        .options(selectinload(Customer.vehicles))
        .where(
            and_(
                Customer.id == customer_id,
                Customer.org_id == current_user.org_id,
            )
        )
    )
    result = await db.execute(query)
    customer = result.scalar_one_or_none()

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )

    return CustomerResponse(
        id=customer.id,
        external_id=customer.external_id,
        first_name=customer.first_name,
        last_name=customer.last_name,
        phone=customer.phone,
        phone_alt=customer.phone_alt,
        email=customer.email,
        address=customer.address,
        city=customer.city,
        state=customer.state,
        zip_code=customer.zip_code,
        preferred_contact_time=customer.preferred_contact_time,
        language_preference=customer.language_preference,
        notes=customer.notes,
        branch_id=customer.branch_id,
        vehicles=[
            VehicleResponse(
                id=v.id,
                vin=v.vin,
                year=v.year,
                make=v.make,
                model=v.model,
                trim=v.trim,
                color=v.color,
                license_plate=v.license_plate,
                mileage=v.mileage,
                last_service_date=v.last_service_date,
                next_service_due=v.next_service_due,
                is_primary=v.is_primary,
            )
            for v in customer.vehicles
        ],
        created_at=customer.created_at,
    )


@router.patch("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: UUID,
    data: CustomerUpdate,
    current_user: User = Depends(require_permission("customers:write")),
    db: AsyncSession = Depends(get_db),
):
    """Update a customer."""
    customer = await db.get(Customer, customer_id)
    if not customer or customer.org_id != current_user.org_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(customer, key, value)

    await db.commit()
    await db.refresh(customer)

    # Reload with vehicles
    query = (
        select(Customer)
        .options(selectinload(Customer.vehicles))
        .where(Customer.id == customer_id)
    )
    result = await db.execute(query)
    customer = result.scalar_one()

    return CustomerResponse(
        id=customer.id,
        external_id=customer.external_id,
        first_name=customer.first_name,
        last_name=customer.last_name,
        phone=customer.phone,
        phone_alt=customer.phone_alt,
        email=customer.email,
        address=customer.address,
        city=customer.city,
        state=customer.state,
        zip_code=customer.zip_code,
        preferred_contact_time=customer.preferred_contact_time,
        language_preference=customer.language_preference,
        notes=customer.notes,
        branch_id=customer.branch_id,
        vehicles=[
            VehicleResponse(
                id=v.id,
                vin=v.vin,
                year=v.year,
                make=v.make,
                model=v.model,
                trim=v.trim,
                color=v.color,
                license_plate=v.license_plate,
                mileage=v.mileage,
                last_service_date=v.last_service_date,
                next_service_due=v.next_service_due,
                is_primary=v.is_primary,
            )
            for v in customer.vehicles
        ],
        created_at=customer.created_at,
    )


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(
    customer_id: UUID,
    current_user: User = Depends(require_permission("customers:write")),
    db: AsyncSession = Depends(get_db),
):
    """Delete a customer."""
    customer = await db.get(Customer, customer_id)
    if not customer or customer.org_id != current_user.org_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )

    await db.delete(customer)
    await db.commit()


@router.post("/{customer_id}/vehicles", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
async def add_vehicle(
    customer_id: UUID,
    data: VehicleCreate,
    current_user: User = Depends(require_permission("customers:write")),
    db: AsyncSession = Depends(get_db),
):
    """Add a vehicle to a customer."""
    customer = await db.get(Customer, customer_id)
    if not customer or customer.org_id != current_user.org_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )

    vehicle = Vehicle(
        customer_id=customer_id,
        vin=data.vin,
        year=data.year,
        make=data.make,
        model=data.model,
        trim=data.trim,
        color=data.color,
        license_plate=data.license_plate,
        mileage=data.mileage,
        last_service_date=data.last_service_date,
        next_service_due=data.next_service_due,
        is_primary=data.is_primary or False,
    )
    db.add(vehicle)
    await db.commit()
    await db.refresh(vehicle)

    return VehicleResponse(
        id=vehicle.id,
        vin=vehicle.vin,
        year=vehicle.year,
        make=vehicle.make,
        model=vehicle.model,
        trim=vehicle.trim,
        color=vehicle.color,
        license_plate=vehicle.license_plate,
        mileage=vehicle.mileage,
        last_service_date=vehicle.last_service_date,
        next_service_due=vehicle.next_service_due,
        is_primary=vehicle.is_primary,
    )
