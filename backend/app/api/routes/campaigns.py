"""
Voice Agent Ops - Campaign Routes
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.db.session import get_db
from app.models import (
    Campaign,
    CampaignStatus,
    CampaignTarget,
    Customer,
    DncEntry,
    TargetStatus,
    Vehicle,
    CallOutcome,
)
from app.schemas import (
    CampaignCreate,
    CampaignListItem,
    CampaignResponse,
    CampaignUpdate,
    MessageResponse,
    PaginatedResponse,
    TargetUploadRequest,
    TargetUploadResult,
)
from app.api.deps import AuthenticatedUser, ManagerOrAdmin
from app.services.elevenlabs_client import ElevenLabsClient

logger = get_logger(__name__)
router = APIRouter(prefix="/campaigns", tags=["Campaigns"])


@router.get("", response_model=PaginatedResponse[CampaignListItem])
async def list_campaigns(
    current_user: AuthenticatedUser,
    db: AsyncSession = Depends(get_db),
    branch_id: Optional[UUID] = Query(None),
    status_filter: Optional[CampaignStatus] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> PaginatedResponse[CampaignListItem]:
    """List campaigns with filtering."""
    query = select(Campaign).where(Campaign.org_id == current_user.org_id)

    if branch_id:
        query = query.where(Campaign.branch_id == branch_id)
    if status_filter:
        query = query.where(Campaign.status == status_filter)

    # Count total
    count_result = await db.execute(
        select(func.count()).select_from(query.subquery())
    )
    total = count_result.scalar() or 0

    # Pagination
    offset = (page - 1) * page_size
    query = query.order_by(Campaign.created_at.desc()).offset(offset).limit(page_size)

    result = await db.execute(query)
    campaigns = result.scalars().all()

    # Get target stats for each campaign
    items = []
    for campaign in campaigns:
        stats = await _get_campaign_stats(db, campaign.id)
        items.append(
            CampaignListItem(
                id=campaign.id,
                name=campaign.name,
                purpose=campaign.purpose,
                status=campaign.status,
                branch_id=campaign.branch_id,
                created_at=campaign.created_at,
                **stats,
            )
        )

    pages = (total + page_size - 1) // page_size

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: UUID,
    current_user: AuthenticatedUser,
    db: AsyncSession = Depends(get_db),
) -> CampaignResponse:
    """Get campaign details."""
    result = await db.execute(
        select(Campaign).where(
            Campaign.id == campaign_id,
            Campaign.org_id == current_user.org_id,
        )
    )
    campaign = result.scalar_one_or_none()

    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found",
        )

    stats = await _get_campaign_stats(db, campaign.id)

    return CampaignResponse(
        id=campaign.id,
        org_id=campaign.org_id,
        branch_id=campaign.branch_id,
        name=campaign.name,
        purpose=campaign.purpose,
        script_id=campaign.script_id,
        status=campaign.status,
        schedule_window_json=campaign.schedule_window_json,
        retry_policy_json=campaign.retry_policy_json,
        voice_config_json=campaign.voice_config_json,
        eleven_batch_id=campaign.eleven_batch_id,
        created_at=campaign.created_at,
        updated_at=campaign.updated_at,
        **stats,
    )


@router.post("", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    request: CampaignCreate,
    current_user: ManagerOrAdmin,
    db: AsyncSession = Depends(get_db),
) -> CampaignResponse:
    """Create a new campaign."""
    campaign = Campaign(
        org_id=current_user.org_id,
        branch_id=request.branch_id,
        name=request.name,
        purpose=request.purpose,
        script_id=request.script_id,
        status=CampaignStatus.DRAFT,
        schedule_window_json=request.schedule_window.model_dump() if request.schedule_window else None,
        retry_policy_json=request.retry_policy.model_dump() if request.retry_policy else None,
        voice_config_json=request.voice_config.model_dump() if request.voice_config else None,
    )
    db.add(campaign)
    await db.commit()
    await db.refresh(campaign)

    logger.info(f"Campaign created: {campaign.name} by {current_user.email}")

    return CampaignResponse(
        id=campaign.id,
        org_id=campaign.org_id,
        branch_id=campaign.branch_id,
        name=campaign.name,
        purpose=campaign.purpose,
        script_id=campaign.script_id,
        status=campaign.status,
        schedule_window_json=campaign.schedule_window_json,
        retry_policy_json=campaign.retry_policy_json,
        voice_config_json=campaign.voice_config_json,
        eleven_batch_id=campaign.eleven_batch_id,
        created_at=campaign.created_at,
        updated_at=campaign.updated_at,
        total_targets=0,
        pending_targets=0,
        completed_targets=0,
        booked_count=0,
    )


@router.post("/{campaign_id}/upload-targets", response_model=TargetUploadResult)
async def upload_targets(
    campaign_id: UUID,
    request: TargetUploadRequest,
    current_user: ManagerOrAdmin,
    db: AsyncSession = Depends(get_db),
) -> TargetUploadResult:
    """Upload targets to a campaign."""
    # Verify campaign exists and belongs to org
    result = await db.execute(
        select(Campaign).where(
            Campaign.id == campaign_id,
            Campaign.org_id == current_user.org_id,
        )
    )
    campaign = result.scalar_one_or_none()

    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found",
        )

    if campaign.status not in [CampaignStatus.DRAFT, CampaignStatus.READY]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot add targets to a running campaign",
        )

    created = 0
    skipped_dnc = 0
    skipped_duplicate = 0
    errors = []

    for item in request.targets:
        try:
            # Check DNC list
            dnc_result = await db.execute(
                select(DncEntry).where(
                    DncEntry.org_id == current_user.org_id,
                    DncEntry.phone_e164 == item.phone,
                )
            )
            if dnc_result.scalar_one_or_none():
                skipped_dnc += 1
                continue

            # Find or create customer
            customer_result = await db.execute(
                select(Customer).where(
                    Customer.org_id == current_user.org_id,
                    Customer.phone_e164 == item.phone,
                )
            )
            customer = customer_result.scalar_one_or_none()

            if not customer:
                customer = Customer(
                    org_id=current_user.org_id,
                    first_name=item.first_name,
                    last_name=item.last_name,
                    phone_e164=item.phone,
                )
                db.add(customer)
                await db.flush()

            # Find or create vehicle if plate provided
            vehicle = None
            if item.plate_number:
                vehicle_result = await db.execute(
                    select(Vehicle).where(
                        Vehicle.org_id == current_user.org_id,
                        Vehicle.plate_number == item.plate_number,
                    )
                )
                vehicle = vehicle_result.scalar_one_or_none()

                if not vehicle and item.vehicle_make and item.vehicle_model:
                    vehicle = Vehicle(
                        org_id=current_user.org_id,
                        customer_id=customer.id,
                        make=item.vehicle_make,
                        model=item.vehicle_model,
                        plate_number=item.plate_number,
                    )
                    db.add(vehicle)
                    await db.flush()

            # Check for duplicate target
            existing_target = await db.execute(
                select(CampaignTarget).where(
                    CampaignTarget.campaign_id == campaign_id,
                    CampaignTarget.customer_id == customer.id,
                )
            )
            if existing_target.scalar_one_or_none():
                skipped_duplicate += 1
                continue

            # Create target
            target = CampaignTarget(
                campaign_id=campaign_id,
                customer_id=customer.id,
                vehicle_id=vehicle.id if vehicle else None,
                job_id=item.job_id,
                status=TargetStatus.PENDING,
            )
            db.add(target)
            created += 1

        except Exception as e:
            errors.append(f"Error processing {item.phone}: {str(e)}")

    # Update campaign status to READY if it has targets
    if created > 0 and campaign.status == CampaignStatus.DRAFT:
        campaign.status = CampaignStatus.READY

    await db.commit()

    logger.info(f"Uploaded {created} targets to campaign {campaign_id}")

    return TargetUploadResult(
        total_received=len(request.targets),
        created=created,
        skipped_dnc=skipped_dnc,
        skipped_duplicate=skipped_duplicate,
        errors=errors,
    )


@router.post("/{campaign_id}/start", response_model=MessageResponse)
async def start_campaign(
    campaign_id: UUID,
    current_user: ManagerOrAdmin,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Start a campaign - triggers ElevenLabs batch calling."""
    result = await db.execute(
        select(Campaign).where(
            Campaign.id == campaign_id,
            Campaign.org_id == current_user.org_id,
        )
    )
    campaign = result.scalar_one_or_none()

    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found",
        )

    if campaign.status not in [CampaignStatus.READY, CampaignStatus.PAUSED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot start campaign with status: {campaign.status.value}",
        )

    # Get pending targets with customer info
    targets_result = await db.execute(
        select(CampaignTarget, Customer, Vehicle)
        .join(Customer, CampaignTarget.customer_id == Customer.id)
        .outerjoin(Vehicle, CampaignTarget.vehicle_id == Vehicle.id)
        .where(
            CampaignTarget.campaign_id == campaign_id,
            CampaignTarget.status == TargetStatus.PENDING,
        )
    )
    targets = targets_result.all()

    if not targets:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No pending targets to call",
        )

    # Prepare recipients for ElevenLabs
    recipients = []
    for target, customer, vehicle in targets:
        recipients.append({
            "phone_number": customer.phone_e164,
            "metadata": {
                "target_id": str(target.id),
                "customer_id": str(customer.id),
                "customer_name": customer.full_name,
                "vehicle_model": vehicle.display_name if vehicle else None,
                "plate_number": vehicle.plate_number if vehicle else None,
            },
        })

    # Call ElevenLabs API
    try:
        client = ElevenLabsClient()
        batch_result = await client.create_batch_call(
            campaign_id=str(campaign.id),
            recipients=recipients,
            script_id=str(campaign.script_id) if campaign.script_id else None,
        )

        # Update campaign
        campaign.status = CampaignStatus.RUNNING
        campaign.eleven_batch_id = batch_result.get("batch_id")

        # Mark targets as in progress
        for target, _, _ in targets:
            target.status = TargetStatus.IN_PROGRESS

        await db.commit()

        logger.info(f"Started campaign {campaign_id} with {len(recipients)} recipients")

        return MessageResponse(message=f"Campaign started with {len(recipients)} calls")

    except Exception as e:
        logger.error(f"Failed to start campaign: {e}")
        campaign.status = CampaignStatus.FAILED
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start campaign: {str(e)}",
        )


@router.post("/{campaign_id}/pause", response_model=MessageResponse)
async def pause_campaign(
    campaign_id: UUID,
    current_user: ManagerOrAdmin,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Pause a running campaign."""
    result = await db.execute(
        select(Campaign).where(
            Campaign.id == campaign_id,
            Campaign.org_id == current_user.org_id,
        )
    )
    campaign = result.scalar_one_or_none()

    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found",
        )

    if campaign.status != CampaignStatus.RUNNING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Campaign is not running",
        )

    campaign.status = CampaignStatus.PAUSED
    await db.commit()

    logger.info(f"Paused campaign {campaign_id}")

    return MessageResponse(message="Campaign paused")


@router.post("/{campaign_id}/resume", response_model=MessageResponse)
async def resume_campaign(
    campaign_id: UUID,
    current_user: ManagerOrAdmin,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Resume a paused campaign."""
    return await start_campaign(campaign_id, current_user, db)


async def _get_campaign_stats(db: AsyncSession, campaign_id: UUID) -> dict:
    """Get campaign target statistics."""
    result = await db.execute(
        select(
            func.count(CampaignTarget.id).label("total"),
            func.count(CampaignTarget.id).filter(
                CampaignTarget.status == TargetStatus.PENDING
            ).label("pending"),
            func.count(CampaignTarget.id).filter(
                CampaignTarget.status == TargetStatus.DONE
            ).label("completed"),
            func.count(CampaignTarget.id).filter(
                CampaignTarget.last_outcome == CallOutcome.BOOKED
            ).label("booked"),
        ).where(CampaignTarget.campaign_id == campaign_id)
    )
    row = result.first()

    return {
        "total_targets": row.total or 0,
        "pending_targets": row.pending or 0,
        "completed_targets": row.completed or 0,
        "booked_count": row.booked or 0,
    }
