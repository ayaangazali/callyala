"""
Voice Agent Ops - Analytics Schemas
"""

from datetime import datetime
from typing import Any

from pydantic import Field

from app.schemas.base import BaseSchema


class KPIStats(BaseSchema):
    """Overview KPI statistics."""

    calls_placed: int = 0
    answer_rate: float = 0.0  # percentage
    booked_pickups: int = 0
    reschedules: int = 0
    human_followups: int = 0
    avg_duration_sec: int = 0

    # Change indicators (vs previous period)
    calls_placed_change: float = 0.0
    answer_rate_change: float = 0.0
    booked_pickups_change: float = 0.0


class HourlyBucket(BaseSchema):
    """Hourly data bucket for charts."""

    hour: str  # ISO format or HH:00
    timestamp: datetime
    count: int = 0


class CallsOverTimeData(BaseSchema):
    """Calls over time chart data."""

    buckets: list[HourlyBucket]
    total: int = 0


class OutcomeBreakdown(BaseSchema):
    """Outcome breakdown for pie/donut chart."""

    outcome: str
    count: int
    percentage: float


class OutcomesChartData(BaseSchema):
    """Outcomes breakdown chart data."""

    outcomes: list[OutcomeBreakdown]
    total: int = 0


class OverviewResponse(BaseSchema):
    """Complete overview dashboard response."""

    kpis: KPIStats
    calls_over_time: CallsOverTimeData
    outcomes: OutcomesChartData
    period_start: datetime
    period_end: datetime


class NeedsAttentionItem(BaseSchema):
    """Item requiring human attention."""

    id: str  # call_id or target_id
    type: str  # "call" or "target"
    reason: str
    priority: str  # "high", "medium", "low"
    customer_name: str
    phone: str
    vehicle: str | None = None
    created_at: datetime
    details: dict[str, Any] | None = None


class NeedsAttentionResponse(BaseSchema):
    """Needs attention list response."""

    items: list[NeedsAttentionItem]
    total: int
