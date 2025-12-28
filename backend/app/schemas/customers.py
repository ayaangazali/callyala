"""
Voice Agent Ops - Customer & Vehicle Schemas
"""

from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import Field

from app.schemas.base import BaseSchema, IDMixin, TimestampMixin


class VehicleBase(BaseSchema):
    """Base vehicle fields."""

    vin: Optional[str] = None
    year: Optional[int] = None
    make: Optional[str] = None
    model: Optional[str] = None
    trim: Optional[str] = None
    color: Optional[str] = None
    license_plate: Optional[str] = None
    mileage: Optional[int] = None
    last_service_date: Optional[date] = None
    next_service_due: Optional[date] = None
    is_primary: bool = False


class VehicleCreate(VehicleBase):
    """Create vehicle request."""
    pass


class VehicleResponse(VehicleBase, IDMixin):
    """Vehicle response."""
    pass


class CustomerBase(BaseSchema):
    """Base customer fields."""

    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    phone: str = Field(min_length=10, max_length=20)
    phone_alt: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    preferred_contact_time: Optional[str] = None
    language_preference: str = "en"
    notes: Optional[str] = None


class CustomerCreate(CustomerBase):
    """Create customer request."""

    external_id: Optional[str] = None
    branch_id: Optional[UUID] = None


class CustomerUpdate(BaseSchema):
    """Update customer request."""

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    phone_alt: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    preferred_contact_time: Optional[str] = None
    language_preference: Optional[str] = None
    notes: Optional[str] = None


class CustomerResponse(CustomerBase, IDMixin, TimestampMixin):
    """Customer response."""

    external_id: Optional[str] = None
    branch_id: Optional[UUID] = None
    vehicles: list[VehicleResponse] = []

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


class CustomerListResponse(BaseSchema):
    """Paginated customer list response."""

    items: list[CustomerResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
    year: int | None = None
    color: str | None = None


class VehicleCreate(VehicleBase):
    """Create vehicle request."""

    customer_id: UUID


class VehicleUpdate(BaseSchema):
    """Update vehicle request."""

    make: str | None = None
    model: str | None = None
    plate_number: str | None = None
    vin: str | None = None
    year: int | None = None
    color: str | None = None


class VehicleResponse(VehicleBase, IDMixin, TimestampMixin):
    """Vehicle response."""

    org_id: UUID
    customer_id: UUID

    @property
    def display_name(self) -> str:
        year_str = f"{self.year} " if self.year else ""
        return f"{year_str}{self.make} {self.model}"


class VehicleListItem(BaseSchema, IDMixin):
    """Vehicle list item."""

    make: str
    model: str
    plate_number: str
    year: int | None
    customer_name: str | None = None
