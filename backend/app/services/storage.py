"""Local JSON file storage service."""

from datetime import datetime
from typing import Optional
import uuid

from app.core.config import settings
from app.core.files import atomic_write_json, read_json, append_jsonl, read_jsonl
from app.core.logging import logger
from app.core.time import now_utc
from app.models import Campaign, Call, CallStatus, CampaignStatus


class StorageService:
    """Handles all local file persistence."""

    # ─────────────────────────────────────────────────────────────────────
    # Campaigns
    # ─────────────────────────────────────────────────────────────────────

    def get_campaigns(self) -> list[Campaign]:
        """Get all campaigns."""
        data = read_json(settings.campaigns_file, default={"campaigns": []})
        return [Campaign(**c) for c in data.get("campaigns", [])]

    def get_campaign(self, campaign_id: str) -> Optional[Campaign]:
        """Get campaign by ID."""
        campaigns = self.get_campaigns()
        for c in campaigns:
            if c.id == campaign_id:
                return c
        return None

    def create_campaign(self, campaign: Campaign) -> Campaign:
        """Create a new campaign."""
        data = read_json(settings.campaigns_file, default={"campaigns": []})
        data["campaigns"].append(campaign.model_dump(mode="json"))
        atomic_write_json(settings.campaigns_file, data)
        logger.info(f"Created campaign {campaign.id}: {campaign.name}")
        return campaign

    def update_campaign(self, campaign: Campaign) -> Campaign:
        """Update an existing campaign."""
        data = read_json(settings.campaigns_file, default={"campaigns": []})
        campaigns = data.get("campaigns", [])
        
        for i, c in enumerate(campaigns):
            if c["id"] == campaign.id:
                campaigns[i] = campaign.model_dump(mode="json")
                break
        
        data["campaigns"] = campaigns
        atomic_write_json(settings.campaigns_file, data)
        logger.info(f"Updated campaign {campaign.id}")
        return campaign

    def delete_campaign(self, campaign_id: str) -> bool:
        """Delete a campaign."""
        data = read_json(settings.campaigns_file, default={"campaigns": []})
        campaigns = data.get("campaigns", [])
        original_len = len(campaigns)
        
        campaigns = [c for c in campaigns if c["id"] != campaign_id]
        
        if len(campaigns) < original_len:
            data["campaigns"] = campaigns
            atomic_write_json(settings.campaigns_file, data)
            logger.info(f"Deleted campaign {campaign_id}")
            return True
        return False

    # ─────────────────────────────────────────────────────────────────────
    # Calls
    # ─────────────────────────────────────────────────────────────────────

    def get_calls(
        self,
        campaign_id: Optional[str] = None,
        status: Optional[CallStatus] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Call]:
        """Get calls with optional filtering."""
        calls = read_jsonl(settings.calls_file)
        
        # Filter
        if campaign_id:
            calls = [c for c in calls if c.get("campaign_id") == campaign_id]
        if status:
            calls = [c for c in calls if c.get("status") == status.value]
        
        # Sort by created_at descending
        calls.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        # Paginate
        calls = calls[offset : offset + limit]
        
        return [Call(**c) for c in calls]

    def get_call(self, call_id: str) -> Optional[Call]:
        """Get call by ID using the index."""
        index = read_json(settings.call_index_file, default={})
        if call_id not in index:
            return None
        
        # For simplicity, scan the JSONL file
        # In production, you'd store line offsets in the index
        calls = read_jsonl(settings.calls_file)
        for c in calls:
            if c.get("id") == call_id:
                return Call(**c)
        return None

    def get_call_by_elevenlabs_id(self, elevenlabs_call_id: str) -> Optional[Call]:
        """Get call by ElevenLabs call ID."""
        calls = read_jsonl(settings.calls_file)
        for c in calls:
            if c.get("elevenlabs_call_id") == elevenlabs_call_id:
                return Call(**c)
        return None

    def create_call(self, call: Call) -> Call:
        """Create a new call record."""
        # Append to JSONL
        append_jsonl(settings.calls_file, call.model_dump(mode="json"))
        
        # Update index
        index = read_json(settings.call_index_file, default={})
        index[call.id] = {
            "campaign_id": call.campaign_id,
            "created_at": call.created_at.isoformat(),
        }
        atomic_write_json(settings.call_index_file, index)
        
        logger.debug(f"Created call {call.id}")
        return call

    def update_call(self, call: Call) -> Call:
        """Update a call record (rewrite JSONL - expensive!)."""
        calls = read_jsonl(settings.calls_file)
        
        for i, c in enumerate(calls):
            if c.get("id") == call.id:
                calls[i] = call.model_dump(mode="json")
                break
        
        # Rewrite entire file (for MVP simplicity)
        settings.calls_file.unlink(missing_ok=True)
        for c in calls:
            append_jsonl(settings.calls_file, c)
        
        logger.debug(f"Updated call {call.id}")
        return call

    def create_calls_batch(self, calls: list[Call]) -> list[Call]:
        """Create multiple calls efficiently."""
        index = read_json(settings.call_index_file, default={})
        
        for call in calls:
            append_jsonl(settings.calls_file, call.model_dump(mode="json"))
            index[call.id] = {
                "campaign_id": call.campaign_id,
                "created_at": call.created_at.isoformat(),
            }
        
        atomic_write_json(settings.call_index_file, index)
        logger.info(f"Created {len(calls)} calls in batch")
        return calls

    # ─────────────────────────────────────────────────────────────────────
    # Webhook Deduplication
    # ─────────────────────────────────────────────────────────────────────

    def check_webhook_processed(self, webhook_id: str) -> bool:
        """Check if webhook was already processed."""
        dedup = read_json(settings.webhook_dedup_file, default={})
        return webhook_id in dedup

    def mark_webhook_processed(self, webhook_id: str) -> None:
        """Mark webhook as processed."""
        dedup = read_json(settings.webhook_dedup_file, default={})
        dedup[webhook_id] = now_utc().isoformat()
        
        # Keep only last 10000 entries
        if len(dedup) > 10000:
            sorted_items = sorted(dedup.items(), key=lambda x: x[1], reverse=True)
            dedup = dict(sorted_items[:10000])
        
        atomic_write_json(settings.webhook_dedup_file, dedup)

    # ─────────────────────────────────────────────────────────────────────
    # Statistics
    # ─────────────────────────────────────────────────────────────────────

    def get_call_stats(self, campaign_id: Optional[str] = None) -> dict:
        """Get aggregated call statistics."""
        calls = read_jsonl(settings.calls_file)
        
        if campaign_id:
            calls = [c for c in calls if c.get("campaign_id") == campaign_id]
        
        stats = {
            "total": len(calls),
            "by_status": {},
            "by_outcome": {},
            "total_duration_seconds": 0,
            "avg_duration_seconds": 0,
        }
        
        completed_count = 0
        for c in calls:
            status = c.get("status", "unknown")
            outcome = c.get("outcome", "unknown")
            duration = c.get("duration_seconds", 0) or 0
            
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
            stats["by_outcome"][outcome] = stats["by_outcome"].get(outcome, 0) + 1
            stats["total_duration_seconds"] += duration
            
            if status == "completed":
                completed_count += 1
        
        if completed_count > 0:
            stats["avg_duration_seconds"] = stats["total_duration_seconds"] / completed_count
        
        return stats


# Singleton instance
storage = StorageService()
