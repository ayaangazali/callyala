"""Calls endpoints."""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query

from app.services.storage import storage
from app.models import CallStatus

router = APIRouter(prefix="/api/calls", tags=["calls"])


@router.get("")
async def list_calls(
    campaign_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(100, le=500),
    offset: int = Query(0),
):
    """List calls with optional filtering."""
    status_filter = CallStatus(status) if status else None
    calls = storage.get_calls(
        campaign_id=campaign_id,
        status=status_filter,
        limit=limit,
        offset=offset,
    )
    return {"calls": [c.model_dump(mode="json") for c in calls], "count": len(calls)}


@router.get("/{call_id}")
async def get_call(call_id: str):
    """Get call details."""
    call = storage.get_call(call_id)
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    return call.model_dump(mode="json")


@router.get("/{call_id}/transcript")
async def get_call_transcript(call_id: str):
    """Get call transcript."""
    call = storage.get_call(call_id)
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    return {"call_id": call_id, "transcript": call.transcript or ""}
