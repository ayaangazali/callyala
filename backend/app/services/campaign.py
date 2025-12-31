"""Campaign orchestration service."""

import uuid
from typing import Any, Optional

from app.core.config import settings
from app.core.logging import logger
from app.core.time import now_utc
from app.models import Campaign, Call, CallStatus, CampaignStatus, SheetRow
from app.services.storage import storage
from app.services.sheets import sheets
from app.services.elevenlabs import elevenlabs


class CampaignService:
    """Orchestrates campaign creation and execution."""

    def create_from_sheet(
        self,
        name: str,
        sheet_id: Optional[str] = None,
        sheet_range: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Campaign:
        """Create a campaign from a Google Sheet."""
        sheet_id = sheet_id or settings.google_sheets_spreadsheet_id
        sheet_range = sheet_range or settings.google_sheets_range
        
        # Read leads from sheet
        rows = sheets.read_sheet(sheet_id, sheet_range, use_cache=False)
        
        campaign = Campaign(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            sheet_id=sheet_id,
            sheet_range=sheet_range,
            agent_id=settings.elevenlabs_agent_id,
            phone_number_id=settings.elevenlabs_phone_number_id,
            total_leads=len(rows),
            created_at=now_utc(),
        )
        
        storage.create_campaign(campaign)
        
        # Create call records for each lead
        calls = []
        for row in rows:
            call = Call(
                id=str(uuid.uuid4()),
                campaign_id=campaign.id,
                row_number=row.row_number,
                phone=row.phone,
                customer_name=row.full_name,
                created_at=now_utc(),
                metadata={"vehicle_interest": row.vehicle_interest, "email": row.email},
            )
            calls.append(call)
        
        if calls:
            storage.create_calls_batch(calls)
        
        logger.info(f"Created campaign '{name}' with {len(calls)} leads")
        return campaign

    async def start_campaign(self, campaign_id: str) -> dict[str, Any]:
        """Start calling for a campaign."""
        campaign = storage.get_campaign(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign {campaign_id} not found")
        
        if campaign.status == CampaignStatus.RUNNING:
            raise ValueError("Campaign is already running")
        
        # Update status
        campaign.status = CampaignStatus.RUNNING
        campaign.started_at = now_utc()
        storage.update_campaign(campaign)
        
        # Get pending calls
        calls = storage.get_calls(campaign_id=campaign_id, status=CallStatus.PENDING, limit=campaign.batch_size)
        
        if not calls:
            campaign.status = CampaignStatus.COMPLETED
            campaign.completed_at = now_utc()
            storage.update_campaign(campaign)
            return {"status": "completed", "message": "No pending calls"}
        
        # Prepare batch
        batch_data = []
        for call in calls:
            batch_data.append({
                "internal_call_id": call.id,
                "phone": call.phone,
                "customer_name": call.customer_name,
                "first_name": call.customer_name.split()[0] if call.customer_name else "",
                "vehicle_interest": call.metadata.get("vehicle_interest", ""),
            })
        
        # Initiate calls
        results = await elevenlabs.initiate_batch_calls(
            calls=batch_data,
            agent_id=campaign.agent_id,
            phone_number_id=campaign.phone_number_id,
        )
        
        # Update call records
        queued = 0
        failed = 0
        for result in results:
            internal_id = result.get("internal_call_id")
            if not internal_id:
                continue
            
            call = storage.get_call(internal_id)
            if not call:
                continue
            
            if result.get("error"):
                call.status = CallStatus.FAILED
                call.error_message = result.get("error")
                failed += 1
            else:
                call.status = CallStatus.QUEUED
                call.elevenlabs_call_id = result.get("call_id")
                call.queued_at = now_utc()
                queued += 1
            
            storage.update_call(call)
        
        # Update campaign stats
        campaign.calls_made += queued
        storage.update_campaign(campaign)
        
        logger.info(f"Campaign {campaign_id}: queued {queued}, failed {failed}")
        return {"status": "running", "queued": queued, "failed": failed}

    def pause_campaign(self, campaign_id: str) -> Campaign:
        """Pause a running campaign."""
        campaign = storage.get_campaign(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign {campaign_id} not found")
        
        campaign.status = CampaignStatus.PAUSED
        return storage.update_campaign(campaign)

    def get_campaign_progress(self, campaign_id: str) -> dict[str, Any]:
        """Get campaign progress."""
        campaign = storage.get_campaign(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign {campaign_id} not found")
        
        calls = storage.get_calls(campaign_id=campaign_id, limit=10000)
        
        return {
            "campaign": campaign.model_dump(mode="json"),
            "progress": {
                "total": campaign.total_leads,
                "completed": sum(1 for c in calls if c.status == CallStatus.COMPLETED),
                "pending": sum(1 for c in calls if c.status == CallStatus.PENDING),
                "in_progress": sum(1 for c in calls if c.status in [CallStatus.QUEUED, CallStatus.IN_PROGRESS]),
                "failed": sum(1 for c in calls if c.status == CallStatus.FAILED),
            },
        }


campaign_service = CampaignService()
