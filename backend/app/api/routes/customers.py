"""Customer management API endpoints."""

from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

router = APIRouter(prefix="/api/customers", tags=["customers"])


class VehicleCreate(BaseModel):
    make: str
    model: str
    year: int
    vin: Optional[str] = None
    license_plate: Optional[str] = None


class CreateCustomerRequest(BaseModel):
    name: str
    phone: str
    email: Optional[str] = None
    address: Optional[str] = None
    vehicles: Optional[List[VehicleCreate]] = None


class UpdateCustomerRequest(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    status: Optional[str] = None


customers_db = {}
customer_counter = 1
vehicle_counter = 1


@router.get("")
async def list_customers(
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(100, le=500),
):
    """List all customers with optional filtering."""
    customers = list(customers_db.values())
    
    if search:
        search_lower = search.lower()
        customers = [
            c for c in customers
            if search_lower in c["name"].lower()
            or search_lower in c["phone"]
        ]
    
    if status:
        customers = [c for c in customers if c["status"] == status]
    
    customers = customers[:limit]
    
    return {
        "customers": customers,
        "count": len(customers),
        "total": len(customers_db)
    }


@router.post("")
async def create_customer(req: CreateCustomerRequest):
    """Create a new customer."""
    global customer_counter, vehicle_counter
    
    customer_id = f"cust-{customer_counter:04d}"
    customer_counter += 1
    
    vehicles = []
    if req.vehicles:
        for vehicle_data in req.vehicles:
            vehicle_id = f"veh-{vehicle_counter:04d}"
            vehicle_counter += 1
            vehicle = {
                "id": vehicle_id,
                "customer_id": customer_id,
                **vehicle_data.model_dump(),
                "created_at": datetime.now().isoformat(),
            }
            vehicles.append(vehicle)
    
    customer = {
        "id": customer_id,
        "name": req.name,
        "phone": req.phone,
        "email": req.email,
        "address": req.address,
        "vehicles": vehicles,
        "status": "active",
        "created_at": datetime.now().isoformat(),
    }
    
    customers_db[customer_id] = customer
    
    return {
        **customer,
        "message": "Customer created successfully",
    }


@router.get("/{customer_id}")
async def get_customer(customer_id: str):
    """Get customer by ID."""
    customer = customers_db.get(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.put("/{customer_id}")
async def update_customer(customer_id: str, req: UpdateCustomerRequest):
    """Update a customer."""
    customer = customers_db.get(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    update_data = req.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        customer[key] = value
    
    customer["updated_at"] = datetime.now().isoformat()
    customers_db[customer_id] = customer
    
    return {
        **customer,
        "message": "Customer updated successfully",
    }


@router.delete("/{customer_id}")
async def delete_customer(customer_id: str):
    """Delete a customer."""
    customer = customers_db.get(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    del customers_db[customer_id]
    
    return {
        "id": customer_id,
        "message": "Customer deleted successfully",
    }


@router.get("/vehicles/all")
async def list_all_vehicles(limit: int = Query(100, le=500)):
    """List all vehicles across all customers."""
    all_vehicles = []
    
    for customer in customers_db.values():
        for vehicle in customer.get("vehicles", []):
            all_vehicles.append({
                **vehicle,
                "customer_name": customer["name"],
                "customer_phone": customer["phone"],
            })
    
    all_vehicles = all_vehicles[:limit]
    
    return {
        "vehicles": all_vehicles,
        "count": len(all_vehicles),
    }


@router.get("/stats/summary")
async def get_customer_stats():
    """Get customer statistics."""
    customers = list(customers_db.values())
    
    total = len(customers)
    active = sum(1 for c in customers if c["status"] == "active")
    inactive = sum(1 for c in customers if c["status"] == "inactive")
    
    total_vehicles = sum(len(c.get("vehicles", [])) for c in customers)
    
    return {
        "total": total,
        "active": active,
        "inactive": inactive,
        "totalVehicles": total_vehicles,
    }
