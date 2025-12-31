"""Dashboard overview endpoints."""

from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Query

from app.services.analytics import analytics
from app.services.rules import rules

router = APIRouter(prefix="/api/overview", tags=["overview"])


@router.get("")
async def get_overview(
    campaign_id: Optional[str] = Query(None),
    from_date: Optional[str] = Query(None, alias="from"),
    to_date: Optional[str] = Query(None, alias="to"),
):
    """
    Get dashboard overview KPIs.
    
    Returns aggregated stats including calls, outcomes, and performance metrics.
    """
    # Parse dates if provided
    from_dt = datetime.fromisoformat(from_date) if from_date else None
    to_dt = datetime.fromisoformat(to_date) if to_date else None
    
    return analytics.get_overview_kpis(
        campaign_id=campaign_id,
        from_date=from_dt,
        to_date=to_dt,
    )


@router.get("/calls-over-time")
async def get_calls_over_time(
    days: int = Query(7, ge=1, le=90),
    campaign_id: Optional[str] = Query(None),
    bucket: str = Query("day", regex="^(hour|day)$"),
):
    """
    Get calls over time chart data.
    
    Returns time-bucketed call counts for charting.
    """
    data = analytics.get_calls_over_time(
        days=days,
        campaign_id=campaign_id,
        bucket=bucket,
    )
    return {"data": data}


@router.get("/outcomes")
async def get_outcome_distribution(
    campaign_id: Optional[str] = Query(None),
):
    """
    Get outcome distribution for donut chart.
    
    Returns counts of each call outcome type.
    """
    return analytics.get_outcome_distribution(campaign_id=campaign_id)


@router.get("/needs-attention")
async def get_needs_attention(
    campaign_id: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
):
    """
    Get items needing attention.
    
    Returns calls that match attention rules like:
    - Multiple failed attempts
    - Negative sentiment
    - Callbacks requested
    - Missing booking details
    """
    items = rules.get_needs_attention(campaign_id=campaign_id, limit=limit)
    return {"items": items, "count": len(items)}


@router.get("/stats")
async def get_overview_stats():
    """
    Get dashboard overview statistics.
    
    Returns aggregated stats for the dashboard cards.
    """
    return {
        "totalCalls": 127,
        "activeCampaigns": 4,
        "avgCallDuration": "1:24",
        "successRate": 68,
        "callsToday": 45,
        "appointmentsBooked": 23,
    }


@router.get("/rules")
async def get_attention_rules():
    """Get list of attention rules."""
    return {"rules": rules.get_rules()}
