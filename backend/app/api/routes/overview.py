"""
Voice Agent Ops - Overview/Analytics Routes
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import and_, case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.db.session import get_db
from app.models import Call, CallOutcome, CallStatus, CampaignTarget
from app.schemas import (
    CallsOverTimeData,
    HourlyBucket,
    KPIStats,
    NeedsAttentionItem,
    NeedsAttentionResponse,
    OutcomeBreakdown,
    OutcomesChartData,
    OverviewResponse,
)
from app.api.deps import AuthenticatedUser

logger = get_logger(__name__)
router = APIRouter(prefix="/overview", tags=["Overview"])


@router.get("", response_model=OverviewResponse)
async def get_overview(
    current_user: AuthenticatedUser,
    db: AsyncSession = Depends(get_db),
    branch_id: Optional[UUID] = Query(None),
    from_date: Optional[datetime] = Query(None, alias="from"),
    to_date: Optional[datetime] = Query(None, alias="to"),
) -> OverviewResponse:
    """
    Get overview dashboard data with KPIs, charts, and metrics.
    """
    # Default date range: last 24 hours
    if not to_date:
        to_date = datetime.now(timezone.utc)
    if not from_date:
        from_date = to_date - timedelta(hours=24)

    # Build base filter
    base_filter = [Call.org_id == current_user.org_id]
    if branch_id:
        base_filter.append(Call.branch_id == branch_id)

    # KPIs
    kpis = await _calculate_kpis(db, base_filter, from_date, to_date)

    # Calls over time (hourly buckets)
    calls_over_time = await _calculate_calls_over_time(db, base_filter, from_date, to_date)

    # Outcomes breakdown
    outcomes = await _calculate_outcomes(db, base_filter, from_date, to_date)

    return OverviewResponse(
        kpis=kpis,
        calls_over_time=calls_over_time,
        outcomes=outcomes,
        period_start=from_date,
        period_end=to_date,
    )


async def _calculate_kpis(
    db: AsyncSession,
    base_filter: list,
    from_date: datetime,
    to_date: datetime,
) -> KPIStats:
    """Calculate KPI statistics."""
    time_filter = and_(
        Call.started_at >= from_date,
        Call.started_at <= to_date,
    )

    # Total calls placed
    calls_result = await db.execute(
        select(func.count(Call.id)).where(
            *base_filter,
            time_filter,
            Call.status.in_([CallStatus.COMPLETED, CallStatus.IN_PROGRESS]),
        )
    )
    calls_placed = calls_result.scalar() or 0

    # Answered calls (completed with outcome)
    answered_result = await db.execute(
        select(func.count(Call.id)).where(
            *base_filter,
            time_filter,
            Call.status == CallStatus.COMPLETED,
            Call.outcome.notin_([CallOutcome.NO_ANSWER, CallOutcome.BUSY]),
        )
    )
    answered = answered_result.scalar() or 0
    answer_rate = (answered / calls_placed * 100) if calls_placed > 0 else 0

    # Booked pickups
    booked_result = await db.execute(
        select(func.count(Call.id)).where(
            *base_filter,
            time_filter,
            Call.outcome == CallOutcome.BOOKED,
        )
    )
    booked_pickups = booked_result.scalar() or 0

    # Reschedules
    rescheduled_result = await db.execute(
        select(func.count(Call.id)).where(
            *base_filter,
            time_filter,
            Call.outcome == CallOutcome.RESCHEDULED,
        )
    )
    reschedules = rescheduled_result.scalar() or 0

    # Human follow-ups required
    followups_result = await db.execute(
        select(func.count(Call.id)).where(
            *base_filter,
            time_filter,
            Call.requires_human_review == True,
        )
    )
    human_followups = followups_result.scalar() or 0

    # Average duration
    avg_duration_result = await db.execute(
        select(func.avg(Call.duration_sec)).where(
            *base_filter,
            time_filter,
            Call.duration_sec.isnot(None),
        )
    )
    avg_duration = int(avg_duration_result.scalar() or 0)

    return KPIStats(
        calls_placed=calls_placed,
        answer_rate=round(answer_rate, 1),
        booked_pickups=booked_pickups,
        reschedules=reschedules,
        human_followups=human_followups,
        avg_duration_sec=avg_duration,
    )


async def _calculate_calls_over_time(
    db: AsyncSession,
    base_filter: list,
    from_date: datetime,
    to_date: datetime,
) -> CallsOverTimeData:
    """Calculate hourly call distribution."""
    # Group by hour
    hour_trunc = func.date_trunc("hour", Call.started_at)

    result = await db.execute(
        select(
            hour_trunc.label("hour"),
            func.count(Call.id).label("count"),
        )
        .where(
            *base_filter,
            Call.started_at >= from_date,
            Call.started_at <= to_date,
        )
        .group_by(hour_trunc)
        .order_by(hour_trunc)
    )

    rows = result.all()
    buckets = [
        HourlyBucket(
            hour=row.hour.strftime("%H:00") if row.hour else "00:00",
            timestamp=row.hour or from_date,
            count=row.count,
        )
        for row in rows
    ]

    total = sum(b.count for b in buckets)

    return CallsOverTimeData(buckets=buckets, total=total)


async def _calculate_outcomes(
    db: AsyncSession,
    base_filter: list,
    from_date: datetime,
    to_date: datetime,
) -> OutcomesChartData:
    """Calculate outcome distribution."""
    result = await db.execute(
        select(
            Call.outcome,
            func.count(Call.id).label("count"),
        )
        .where(
            *base_filter,
            Call.started_at >= from_date,
            Call.started_at <= to_date,
            Call.outcome.isnot(None),
        )
        .group_by(Call.outcome)
    )

    rows = result.all()
    total = sum(row.count for row in rows)

    outcomes = [
        OutcomeBreakdown(
            outcome=row.outcome.value if row.outcome else "OTHER",
            count=row.count,
            percentage=round(row.count / total * 100, 1) if total > 0 else 0,
        )
        for row in rows
    ]

    return OutcomesChartData(outcomes=outcomes, total=total)


@router.get("/needs-attention", response_model=NeedsAttentionResponse)
async def get_needs_attention(
    current_user: AuthenticatedUser,
    db: AsyncSession = Depends(get_db),
    branch_id: Optional[UUID] = Query(None),
    limit: int = Query(20, ge=1, le=100),
) -> NeedsAttentionResponse:
    """
    Get items requiring human attention.
    
    Rules:
    - 3+ failed attempts without booking
    - Callback requested but no callback_time
    - Negative sentiment
    - Booked but missing pickup_time
    """
    items: list[NeedsAttentionItem] = []

    # Rule 1: Multiple failed attempts
    targets_query = (
        select(CampaignTarget)
        .join(Call, CampaignTarget.id == Call.target_id, isouter=True)
        .where(
            CampaignTarget.attempts_count >= 3,
            CampaignTarget.last_outcome != CallOutcome.BOOKED,
        )
        .limit(limit // 4)
    )
    # TODO: Add customer join for names

    # Rule 2: Negative sentiment calls
    negative_calls = await db.execute(
        select(Call)
        .where(
            Call.org_id == current_user.org_id,
            Call.sentiment_score < -0.3,
            Call.requires_human_review == False,
        )
        .order_by(Call.started_at.desc())
        .limit(limit // 4)
    )

    for call in negative_calls.scalars():
        items.append(
            NeedsAttentionItem(
                id=str(call.id),
                type="call",
                reason="Negative sentiment detected",
                priority="high",
                customer_name="",  # TODO: join with customer
                phone="",
                created_at=call.created_at,
            )
        )

    # Rule 3: Requires human review
    review_calls = await db.execute(
        select(Call)
        .where(
            Call.org_id == current_user.org_id,
            Call.requires_human_review == True,
            Call.human_assigned_to.is_(None),
        )
        .order_by(Call.started_at.desc())
        .limit(limit // 2)
    )

    for call in review_calls.scalars():
        items.append(
            NeedsAttentionItem(
                id=str(call.id),
                type="call",
                reason="Requires human review",
                priority="medium",
                customer_name="",
                phone="",
                created_at=call.created_at,
            )
        )

    return NeedsAttentionResponse(items=items, total=len(items))
