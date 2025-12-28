"""
Voice Agent Ops - ElevenLabs Webhook Routes

Handles post-call webhooks from ElevenLabs with signature verification.
"""

import hmac
import hashlib
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging import get_logger
from app.db.session import get_db
from app.models import (
    Appointment,
    AppointmentSource,
    AppointmentStatus,
    AppointmentType,
    AuditLog,
    Call,
    CallDirection,
    CallOutcome,
    CallStatus,
    Campaign,
    CampaignTarget,
    Customer,
    DncEntry,
    SentimentLabel,
    TargetStatus,
)
from app.schemas import ElevenLabsPostCallPayload, MessageResponse

logger = get_logger(__name__)
router = APIRouter(prefix="/webhooks/elevenlabs", tags=["Webhooks"])


def verify_webhook_signature(
    payload: bytes,
    signature: str,
    secret: str,
) -> bool:
    """
    Verify ElevenLabs webhook signature.
    
    Uses HMAC-SHA256 for signature verification.
    """
    if not secret:
        logger.warning("Webhook secret not configured - skipping verification")
        return True

    expected = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected, signature)


def map_sentiment(sentiment_data: dict | None) -> tuple[SentimentLabel | None, float | None]:
    """Map ElevenLabs sentiment to our schema."""
    if not sentiment_data:
        return None, None

    label_map = {
        "positive": SentimentLabel.POS,
        "neutral": SentimentLabel.NEU,
        "negative": SentimentLabel.NEG,
    }

    label = sentiment_data.get("label", "").lower()
    score = sentiment_data.get("score")

    return label_map.get(label), score


def map_call_outcome(analysis: dict | None, status: str | None) -> CallOutcome:
    """Map ElevenLabs analysis to call outcome."""
    if not analysis:
        if status == "no_answer":
            return CallOutcome.NO_ANSWER
        if status == "busy":
            return CallOutcome.BUSY
        if status == "voicemail":
            return CallOutcome.VOICEMAIL
        return CallOutcome.OTHER

    if analysis.get("appointment_booked"):
        return CallOutcome.BOOKED
    if analysis.get("opt_out"):
        return CallOutcome.OPT_OUT
    if analysis.get("callback_requested"):
        return CallOutcome.CALLBACK_REQUESTED

    return CallOutcome.OTHER


@router.post("/post-call", response_model=MessageResponse)
async def handle_post_call_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
    x_elevenlabs_signature: str = Header(None, alias="X-ElevenLabs-Signature"),
) -> MessageResponse:
    """
    Handle ElevenLabs post-call webhook.
    
    Receives call results, transcription, and analysis.
    Creates/updates Call record and related entities.
    """
    # Get raw payload for signature verification
    payload_bytes = await request.body()

    # Verify signature
    if settings.elevenlabs_webhook_secret:
        if not x_elevenlabs_signature:
            logger.warning("Missing webhook signature")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing webhook signature",
            )

        if not verify_webhook_signature(
            payload_bytes,
            x_elevenlabs_signature,
            settings.elevenlabs_webhook_secret,
        ):
            logger.warning("Invalid webhook signature")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid webhook signature",
            )

    # Parse payload
    try:
        payload_dict = await request.json()
        payload = ElevenLabsPostCallPayload.model_validate(payload_dict)
    except Exception as e:
        logger.error(f"Failed to parse webhook payload: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid payload: {e}",
        )

    logger.info(f"Processing webhook for conversation: {payload.conversation_id}")

    # Find existing call by conversation_id or create new
    result = await db.execute(
        select(Call).where(Call.eleven_conversation_id == payload.conversation_id)
    )
    call = result.scalar_one_or_none()

    # If no existing call, try to find campaign target by metadata
    target: CampaignTarget | None = None
    campaign: Campaign | None = None
    customer: Customer | None = None

    if payload.metadata:
        target_id = payload.metadata.get("target_id")
        if target_id:
            target_result = await db.execute(
                select(CampaignTarget).where(CampaignTarget.id == target_id)
            )
            target = target_result.scalar_one_or_none()

            if target:
                campaign_result = await db.execute(
                    select(Campaign).where(Campaign.id == target.campaign_id)
                )
                campaign = campaign_result.scalar_one_or_none()

                customer_result = await db.execute(
                    select(Customer).where(Customer.id == target.customer_id)
                )
                customer = customer_result.scalar_one_or_none()

    # Map analysis to our schema
    analysis_dict = payload.analysis.model_dump() if payload.analysis else {}
    sentiment_label, sentiment_score = map_sentiment(
        payload.sentiment.model_dump() if payload.sentiment else None
    )
    outcome = map_call_outcome(analysis_dict, payload.status)

    if call:
        # Update existing call
        call.status = CallStatus.COMPLETED
        call.outcome = outcome
        call.ended_at = payload.ended_at
        call.duration_sec = payload.duration_seconds
        call.transcript_text = payload.transcript
        call.summary_text = analysis_dict.get("summary")
        call.extracted_fields_json = {
            "pickup_date": analysis_dict.get("pickup_date"),
            "pickup_time": analysis_dict.get("pickup_time"),
            "callback_time": analysis_dict.get("callback_time"),
            "confirmed": analysis_dict.get("customer_confirmed"),
            "notes": analysis_dict.get("notes"),
        }
        call.sentiment_label = sentiment_label
        call.sentiment_score = sentiment_score
        call.recording_url = payload.recording_url

        # Flag for review if negative sentiment or missing data
        if sentiment_score and sentiment_score < -0.3:
            call.requires_human_review = True
        if outcome == CallOutcome.CALLBACK_REQUESTED and not analysis_dict.get("callback_time"):
            call.requires_human_review = True

    else:
        # Create new call record
        if not customer:
            logger.warning(f"Cannot create call without customer context: {payload.conversation_id}")
            # Still acknowledge the webhook
            return MessageResponse(message="Webhook received, but no customer context found")

        call = Call(
            org_id=customer.org_id if customer else None,
            branch_id=campaign.branch_id if campaign else None,
            campaign_id=campaign.id if campaign else None,
            target_id=target.id if target else None,
            customer_id=customer.id if customer else None,
            vehicle_id=target.vehicle_id if target else None,
            job_id=target.job_id if target else None,
            direction=CallDirection.OUTBOUND,
            status=CallStatus.COMPLETED,
            outcome=outcome,
            started_at=payload.started_at,
            ended_at=payload.ended_at,
            duration_sec=payload.duration_seconds,
            eleven_conversation_id=payload.conversation_id,
            eleven_call_id=payload.call_id,
            eleven_batch_id=payload.batch_id,
            transcript_text=payload.transcript,
            summary_text=analysis_dict.get("summary"),
            extracted_fields_json={
                "pickup_date": analysis_dict.get("pickup_date"),
                "pickup_time": analysis_dict.get("pickup_time"),
                "callback_time": analysis_dict.get("callback_time"),
                "confirmed": analysis_dict.get("customer_confirmed"),
                "notes": analysis_dict.get("notes"),
            },
            sentiment_label=sentiment_label,
            sentiment_score=sentiment_score,
            recording_url=payload.recording_url,
            requires_human_review=sentiment_score is not None and sentiment_score < -0.3,
        )
        db.add(call)

    # Update campaign target if exists
    if target:
        target.attempts_count += 1
        target.last_attempt_at = datetime.now(timezone.utc)
        target.last_outcome = outcome

        if outcome == CallOutcome.BOOKED:
            target.status = TargetStatus.DONE
        elif outcome == CallOutcome.OPT_OUT:
            target.status = TargetStatus.OPTED_OUT
        elif target.attempts_count >= 3:  # Max attempts from retry policy
            target.status = TargetStatus.FAILED

    # Handle opt-out: add to DNC
    if outcome == CallOutcome.OPT_OUT and customer:
        existing_dnc = await db.execute(
            select(DncEntry).where(
                DncEntry.org_id == customer.org_id,
                DncEntry.phone_e164 == customer.phone_e164,
            )
        )
        if not existing_dnc.scalar_one_or_none():
            dnc_entry = DncEntry(
                org_id=customer.org_id,
                phone_e164=customer.phone_e164,
                reason="Customer opted out during call",
                source="AI_CALL",
            )
            db.add(dnc_entry)
            logger.info(f"Added {customer.phone_e164} to DNC list")

    # Create appointment if booked
    if outcome == CallOutcome.BOOKED and customer:
        pickup_date = analysis_dict.get("pickup_date")
        pickup_time = analysis_dict.get("pickup_time")

        if pickup_date:
            try:
                # Parse pickup datetime (format varies)
                scheduled_start = datetime.fromisoformat(f"{pickup_date}T{pickup_time or '09:00'}")
            except ValueError:
                scheduled_start = datetime.now(timezone.utc).replace(hour=9, minute=0)

            appointment = Appointment(
                org_id=customer.org_id,
                branch_id=campaign.branch_id if campaign else call.branch_id,
                customer_id=customer.id,
                vehicle_id=target.vehicle_id if target else None,
                job_id=target.job_id if target else None,
                call_id=call.id,
                type=AppointmentType.PICKUP,
                scheduled_start=scheduled_start,
                status=AppointmentStatus.BOOKED,
                source=AppointmentSource.AI,
            )
            db.add(appointment)
            logger.info(f"Created appointment for {customer.full_name}")

    # Create audit log
    if customer:
        audit_log = AuditLog(
            org_id=customer.org_id,
            action="CALL_COMPLETED",
            entity_type="call",
            entity_id=call.id,
            after_json={
                "outcome": outcome.value,
                "conversation_id": payload.conversation_id,
            },
        )
        db.add(audit_log)

    await db.commit()
    logger.info(f"Processed webhook for {payload.conversation_id}: outcome={outcome.value}")

    return MessageResponse(message="Webhook processed successfully")
