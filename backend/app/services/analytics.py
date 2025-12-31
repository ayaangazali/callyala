"""Analytics service for dashboard KPIs and charts."""

from datetime import datetime, timedelta
from typing import Any, Optional
from collections import defaultdict

from app.core.files import read_json, read_jsonl
from app.core.config import settings
from app.core.time import now_utc
from app.models import CallStatus, CallOutcome, CampaignStatus


class AnalyticsService:
    """Compute dashboard analytics from stored data."""

    def get_overview_kpis(
        self,
        campaign_id: Optional[str] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
    ) -> dict[str, Any]:
        """Get main dashboard KPIs."""
        campaigns = read_json(settings.campaigns_file, default={"campaigns": []}).get("campaigns", [])
        calls = read_jsonl(settings.calls_file)
        
        # Filter by campaign
        if campaign_id:
            calls = [c for c in calls if c.get("campaign_id") == campaign_id]
            campaigns = [c for c in campaigns if c.get("id") == campaign_id]
        
        # Filter by date range
        if from_date or to_date:
            filtered = []
            for c in calls:
                created = c.get("created_at")
                if created:
                    try:
                        dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                        if from_date and dt < from_date:
                            continue
                        if to_date and dt > to_date:
                            continue
                        filtered.append(c)
                    except Exception:
                        filtered.append(c)
                else:
                    filtered.append(c)
            calls = filtered
        
        # Campaign stats
        active_campaigns = sum(1 for c in campaigns if c.get("status") == CampaignStatus.RUNNING.value)
        
        # Call stats
        total_calls = len(calls)
        completed_calls = sum(1 for c in calls if c.get("status") == CallStatus.COMPLETED.value)
        queued_calls = sum(1 for c in calls if c.get("status") == CallStatus.QUEUED.value)
        pending_calls = sum(1 for c in calls if c.get("status") == CallStatus.PENDING.value)
        failed_calls = sum(1 for c in calls if c.get("status") == CallStatus.FAILED.value)
        
        # Outcome stats
        appointments = sum(1 for c in calls if c.get("outcome") == CallOutcome.APPOINTMENT_SET.value)
        callbacks = sum(1 for c in calls if c.get("outcome") == CallOutcome.CALLBACK_REQUESTED.value)
        not_interested = sum(1 for c in calls if c.get("outcome") == CallOutcome.NOT_INTERESTED.value)
        voicemails = sum(1 for c in calls if c.get("outcome") == CallOutcome.VOICEMAIL.value)
        opt_outs = sum(1 for c in calls if c.get("outcome") == CallOutcome.DO_NOT_CALL.value)
        
        # Duration stats
        durations = [c.get("duration_seconds", 0) or 0 for c in calls if c.get("status") == CallStatus.COMPLETED.value]
        total_duration = sum(durations)
        avg_duration = total_duration / len(durations) if durations else 0
        
        # Sentiment stats
        negative_sentiment = sum(1 for c in calls if (c.get("sentiment") or "").lower() in ["negative", "neg"])
        
        # Success rate (appointments + callbacks)
        success_rate = (appointments + callbacks) / completed_calls * 100 if completed_calls > 0 else 0
        
        return {
            "campaigns": {
                "total": len(campaigns),
                "active": active_campaigns,
            },
            "calls": {
                "total": total_calls,
                "completed": completed_calls,
                "queued": queued_calls,
                "pending": pending_calls,
                "failed": failed_calls,
            },
            "outcomes": {
                "appointments": appointments,
                "callbacks": callbacks,
                "not_interested": not_interested,
                "voicemails": voicemails,
                "opt_outs": opt_outs,
            },
            "performance": {
                "success_rate": round(success_rate, 1),
                "avg_duration_seconds": round(avg_duration, 1),
                "total_talk_time_minutes": round(total_duration / 60, 1),
                "negative_sentiment_count": negative_sentiment,
            },
        }

    def get_calls_over_time(
        self,
        days: int = 7,
        campaign_id: Optional[str] = None,
        bucket: str = "day",  # "hour" or "day"
    ) -> list[dict[str, Any]]:
        """Get call counts grouped by time bucket."""
        calls = read_jsonl(settings.calls_file)
        
        if campaign_id:
            calls = [c for c in calls if c.get("campaign_id") == campaign_id]
        
        now = now_utc()
        
        if bucket == "hour":
            # Hourly buckets for last 24 hours
            hours = 24
            buckets = {}
            for i in range(hours):
                dt = now - timedelta(hours=i)
                key = dt.strftime("%Y-%m-%d %H:00")
                buckets[key] = {"total": 0, "completed": 0, "appointments": 0}
            
            for call in calls:
                created_at = call.get("created_at", "")
                if created_at:
                    try:
                        dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                        key = dt.strftime("%Y-%m-%d %H:00")
                        if key in buckets:
                            buckets[key]["total"] += 1
                            if call.get("status") == CallStatus.COMPLETED.value:
                                buckets[key]["completed"] += 1
                            if call.get("outcome") == CallOutcome.APPOINTMENT_SET.value:
                                buckets[key]["appointments"] += 1
                    except Exception:
                        pass
        else:
            # Daily buckets
            buckets = {}
            for i in range(days):
                dt = now - timedelta(days=i)
                key = dt.strftime("%Y-%m-%d")
                buckets[key] = {"total": 0, "completed": 0, "appointments": 0}
            
            for call in calls:
                created_at = call.get("created_at", "")
                if created_at:
                    try:
                        dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                        key = dt.strftime("%Y-%m-%d")
                        if key in buckets:
                            buckets[key]["total"] += 1
                            if call.get("status") == CallStatus.COMPLETED.value:
                                buckets[key]["completed"] += 1
                            if call.get("outcome") == CallOutcome.APPOINTMENT_SET.value:
                                buckets[key]["appointments"] += 1
                    except Exception:
                        pass
        
        return [{"time": k, **v} for k, v in sorted(buckets.items())]

    def get_outcome_distribution(
        self,
        campaign_id: Optional[str] = None,
    ) -> dict[str, int]:
        """Get distribution of call outcomes for donut chart."""
        calls = read_jsonl(settings.calls_file)
        
        if campaign_id:
            calls = [c for c in calls if c.get("campaign_id") == campaign_id]
        
        # Only count completed calls
        completed = [c for c in calls if c.get("status") == CallStatus.COMPLETED.value]
        
        distribution = defaultdict(int)
        for call in completed:
            outcome = call.get("outcome", CallOutcome.UNKNOWN.value)
            # Use friendly names
            outcome_name = outcome.replace("_", " ").title()
            distribution[outcome_name] += 1
        
        return dict(distribution)

    def get_campaign_stats(self, campaign_id: str) -> dict[str, Any]:
        """Get detailed stats for a specific campaign."""
        campaigns = read_json(settings.campaigns_file, default={"campaigns": []}).get("campaigns", [])
        calls = read_jsonl(settings.calls_file)
        
        campaign = next((c for c in campaigns if c.get("id") == campaign_id), None)
        if not campaign:
            return {}
        
        campaign_calls = [c for c in calls if c.get("campaign_id") == campaign_id]
        completed = [c for c in campaign_calls if c.get("status") == CallStatus.COMPLETED.value]
        
        # Calculate progress
        total_leads = campaign.get("total_leads", 0)
        progress_pct = (len(completed) / total_leads * 100) if total_leads > 0 else 0
        
        # Duration
        durations = [c.get("duration_seconds", 0) or 0 for c in completed]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        return {
            "campaign": campaign,
            "calls": {
                "total": len(campaign_calls),
                "completed": len(completed),
                "pending": sum(1 for c in campaign_calls if c.get("status") == CallStatus.PENDING.value),
                "queued": sum(1 for c in campaign_calls if c.get("status") == CallStatus.QUEUED.value),
                "failed": sum(1 for c in campaign_calls if c.get("status") == CallStatus.FAILED.value),
            },
            "outcomes": {
                "appointments": sum(1 for c in completed if c.get("outcome") == CallOutcome.APPOINTMENT_SET.value),
                "callbacks": sum(1 for c in completed if c.get("outcome") == CallOutcome.CALLBACK_REQUESTED.value),
                "not_interested": sum(1 for c in completed if c.get("outcome") == CallOutcome.NOT_INTERESTED.value),
                "voicemails": sum(1 for c in completed if c.get("outcome") == CallOutcome.VOICEMAIL.value),
            },
            "performance": {
                "progress_pct": round(progress_pct, 1),
                "avg_duration_seconds": round(avg_duration, 1),
            },
        }


# Singleton instance
analytics = AnalyticsService()
