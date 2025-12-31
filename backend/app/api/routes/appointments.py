"""Appointment management API endpoints."""

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/appointments", tags=["appointments"])


class CreateAppointmentRequest(BaseModel):
    customer_name: str
    customer_phone: str
    customer_email: Optional[str] = None
    date: str
    time: str
    service_type: str
    notes: Optional[str] = None
    vehicle_info: Optional[str] = None


class UpdateAppointmentRequest(BaseModel):
    date: Optional[str] = None
    time: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None


appointments_db = {}
appointment_counter = 1


@router.get("")
async def list_appointments(
    status: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    limit: int = Query(100, le=500),
):
    """List all appointments with optional filtering."""
    appointments = list(appointments_db.values())
    
    if status:
        appointments = [a for a in appointments if a["status"] == status]
    
    if date_from:
        appointments = [a for a in appointments if a["date"] >= date_from]
    
    if date_to:
        appointments = [a for a in appointments if a["date"] <= date_to]
    
    appointments = appointments[:limit]
    
    return {
        "appointments": appointments,
        "count": len(appointments),
        "total": len(appointments_db)
    }


@router.post("")
async def create_appointment(req: CreateAppointmentRequest):
    """Create a new appointment."""
    global appointment_counter
    
    appointment_id = str(appointment_counter)
    appointment_counter += 1
    
    appointment = {
        "id": appointment_id,
        **req.model_dump(),
        "status": "scheduled",
        "created_at": datetime.now().isoformat(),
    }
    
    appointments_db[appointment_id] = appointment
    
    return {
        **appointment,
        "message": "Appointment created successfully",
    }


@router.get("/{appointment_id}")
async def get_appointment(appointment_id: str):
    """Get appointment by ID."""
    appointment = appointments_db.get(appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment


@router.put("/{appointment_id}")
async def update_appointment(appointment_id: str, req: UpdateAppointmentRequest):
    """Update an appointment."""
    appointment = appointments_db.get(appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    update_data = req.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        appointment[key] = value
    
    appointment["updated_at"] = datetime.now().isoformat()
    appointments_db[appointment_id] = appointment
    
    return {
        **appointment,
        "message": "Appointment updated successfully",
    }


@router.delete("/{appointment_id}")
async def cancel_appointment(appointment_id: str):
    """Cancel an appointment."""
    appointment = appointments_db.get(appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    appointment["status"] = "cancelled"
    appointment["cancelled_at"] = datetime.now().isoformat()
    appointments_db[appointment_id] = appointment
    
    return {
        "id": appointment_id,
        "status": "cancelled",
        "message": "Appointment cancelled successfully",
    }


@router.get("/stats/summary")
async def get_appointment_stats():
    """Get appointment statistics."""
    appointments = list(appointments_db.values())
    
    total = len(appointments)
    scheduled = sum(1 for a in appointments if a["status"] == "scheduled")
    confirmed = sum(1 for a in appointments if a["status"] == "confirmed")
    completed = sum(1 for a in appointments if a["status"] == "completed")
    cancelled = sum(1 for a in appointments if a["status"] == "cancelled")
    
    today = datetime.now().date().isoformat()
    today_appointments = [a for a in appointments if a["date"] == today]
    
    return {
        "total": total,
        "scheduled": scheduled,
        "confirmed": confirmed,
        "completed": completed,
        "cancelled": cancelled,
        "today": len(today_appointments),
    }
