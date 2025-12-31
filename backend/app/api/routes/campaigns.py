"""Campaign endpoints."""

from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.storage import storage
from app.services.campaign import campaign_service

router = APIRouter(prefix="/api/campaigns", tags=["campaigns"])


class CreateCampaignRequest(BaseModel):
    name: str
    description: Optional[str] = None
    sheet_id: Optional[str] = None
    sheet_range: Optional[str] = None


@router.get("")
async def list_campaigns():
    """List all campaigns."""
    campaigns = storage.get_campaigns()
    return {"campaigns": [c.model_dump(mode="json") for c in campaigns]}


@router.post("")
async def create_campaign(req: CreateCampaignRequest):
    """Create a new campaign from a Google Sheet."""
    try:
        campaign = campaign_service.create_from_sheet(
            name=req.name,
            description=req.description,
            sheet_id=req.sheet_id,
            sheet_range=req.sheet_range,
        )
        return campaign.model_dump(mode="json")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{campaign_id}")
async def get_campaign(campaign_id: str):
    """Get campaign details."""
    campaign = storage.get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign.model_dump(mode="json")


@router.post("/{campaign_id}/start")
async def start_campaign(campaign_id: str):
    """Start a campaign."""
    try:
        result = await campaign_service.start_campaign(campaign_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{campaign_id}/pause")
async def pause_campaign(campaign_id: str):
    """Pause a campaign."""
    try:
        campaign = campaign_service.pause_campaign(campaign_id)
        return campaign.model_dump(mode="json")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{campaign_id}/progress")
async def get_campaign_progress(campaign_id: str):
    """Get campaign progress."""
    try:
        return campaign_service.get_campaign_progress(campaign_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{campaign_id}")
async def delete_campaign(campaign_id: str):
    """Delete a campaign."""
    if storage.delete_campaign(campaign_id):
        return {"status": "deleted"}
    raise HTTPException(status_code=404, detail="Campaign not found")
