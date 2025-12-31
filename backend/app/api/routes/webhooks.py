"""Webhook endpoints for ElevenLabs callbacks."""

from typing import Any
from fastapi import APIRouter, HTTPException, Header, Request

from app.core.config import settings
from app.core.logging import logger
from app.core.time import now_utc
from app.services.storage import storage
from app.services.sheets import sheets
from app.services.webhook_verify import verify_elevenlabs_signature
from app.models import CallStatus, CallOutcome

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])


def map_outcome(data: dict) -> CallOutcome:
    """Map ElevenLabs analysis to our outcome enum."""
    analysis = data.get("analysis", {})
    intent = (analysis.get("intent") or "").lower()
    
    # Check for specific intents
    if any(x in intent for x in ["appointment", "schedule", "book", "pickup"]):
        return CallOutcome.APPOINTMENT_SET
    elif any(x in intent for x in ["callback", "call back", "call me back"]):
        return CallOutcome.CALLBACK_REQUESTED
    elif any(x in intent for x in ["not interested", "no thanks", "not now"]):
        return CallOutcome.NOT_INTERESTED
    elif "wrong number" in intent:
        return CallOutcome.WRONG_NUMBER
    elif any(x in intent for x in ["voicemail", "leave message"]):
        return CallOutcome.VOICEMAIL
    elif any(x in intent for x in ["do not call", "stop calling", "remove", "opt out"]):
        return CallOutcome.DO_NOT_CALL
    elif "transfer" in intent:
        return CallOutcome.TRANSFERRED
    
    # Check call status
    status = (data.get("status") or data.get("call_status") or "").lower()
    if status in ["no_answer", "no-answer", "noanswer"]:
        return CallOutcome.UNKNOWN
    
    return CallOutcome.UNKNOWN


def extract_booking_info(data: dict) -> dict:
    """Extract booking details from webhook payload."""
    analysis = data.get("analysis", {})
    extracted = data.get("extracted_fields", {})
    
    return {
        "booked_date": extracted.get("pickup_date") or extracted.get("appointment_date") or analysis.get("date"),
        "booked_time": extracted.get("pickup_time") or extracted.get("appointment_time") or analysis.get("time"),
        "confirmed": extracted.get("confirmed", False),
        "callback_time": extracted.get("callback_time"),
        "notes": extracted.get("notes") or analysis.get("notes"),
    }


@router.post("/elevenlabs")
async def elevenlabs_webhook(
    request: Request,
    x_elevenlabs_signature: str = Header(None, alias="X-ElevenLabs-Signature"),
):
    """
    Handle ElevenLabs post-call webhook.
    
    This endpoint:
    1. Verifies the webhook signature
    2. Deduplicates using conversation_id
    3. Updates the local call record
    4. Writes results back to the Google Sheet
    """
    body = await request.body()
    
    # Verify signature (if secret is configured)
    if settings.elevenlabs_webhook_secret and x_elevenlabs_signature:
        if not verify_elevenlabs_signature(body, x_elevenlabs_signature):
            logger.warning("Webhook signature verification failed")
            raise HTTPException(status_code=401, detail="Invalid signature")
    
    data = await request.json()
    
    # Save raw payload for debugging
    logger.debug(f"Received webhook payload: {data}")
    
    # Extract identifiers
    elevenlabs_call_id = data.get("call_id") or data.get("conversation_id")
    if not elevenlabs_call_id:
        logger.warning("Webhook missing call_id/conversation_id")
        return {"status": "ignored", "reason": "no call_id"}
    
    # Check for duplicate (idempotency)
    webhook_id = f"el_{elevenlabs_call_id}"
    if storage.check_webhook_processed(webhook_id):
        logger.info(f"Duplicate webhook for {elevenlabs_call_id}, returning OK")
        return {"status": "duplicate", "call_id": elevenlabs_call_id}
    
    # Find our call record
    call = storage.get_call_by_elevenlabs_id(elevenlabs_call_id)
    if not call:
        # Try to find by metadata
        batch_id = data.get("batch_id")
        if batch_id:
            logger.warning(f"Call not found for ElevenLabs ID {elevenlabs_call_id}, batch {batch_id}")
        else:
            logger.warning(f"Call not found for ElevenLabs ID {elevenlabs_call_id}")
        return {"status": "ignored", "reason": "call not found"}
    
    # Process webhook based on event type
    event_type = data.get("type", "").lower()
    
    if event_type in ["call.completed", "conversation.completed"] or "transcript" in data:
        # Successful call completion
        call.status = CallStatus.COMPLETED
        call.ended_at = now_utc()
        call.transcript = data.get("transcript", "")
        call.summary = data.get("summary", "")
        call.recording_url = data.get("recording_url")
        call.duration_seconds = data.get("duration_seconds") or data.get("duration")
        
        # Determine outcome
        call.outcome = map_outcome(data)
        
        # Extract sentiment
        analysis = data.get("analysis", {})
        call.sentiment = analysis.get("sentiment") or analysis.get("sentiment_label")
        
        # Extract booking info
        booking = extract_booking_info(data)
        call.metadata.update({
            "booked_date": booking["booked_date"],
            "booked_time": booking["booked_time"],
            "confirmed": booking["confirmed"],
            "callback_time": booking["callback_time"],
            "notes": booking["notes"],
        })
        
    elif event_type in ["call.failed", "conversation.failed"]:
        call.status = CallStatus.FAILED
        call.error_message = data.get("error") or data.get("failure_reason") or "Call failed"
        call.ended_at = now_utc()
        
    elif event_type in ["call.no_answer", "no_answer"]:
        call.status = CallStatus.NO_ANSWER
        call.ended_at = now_utc()
        
    elif event_type in ["call.busy", "busy"]:
        call.status = CallStatus.BUSY
        call.ended_at = now_utc()
    
    else:
        # Unknown event, still update if we have useful data
        if data.get("transcript"):
            call.transcript = data.get("transcript")
        if data.get("summary"):
            call.summary = data.get("summary")
        call.ended_at = now_utc()
    
    # Save updated call
    storage.update_call(call)
    
    # Mark webhook as processed
    storage.mark_webhook_processed(webhook_id)
    
    # Update campaign stats
    campaign = storage.get_campaign(call.campaign_id)
    if campaign:
        campaign.calls_completed += 1
        if call.outcome in [CallOutcome.APPOINTMENT_SET, CallOutcome.CALLBACK_REQUESTED]:
            campaign.calls_successful += 1
        storage.update_campaign(campaign)
    
    # Write back to Google Sheet
    try:
        sheet_updates = {
            "status": call.status.value,
            "outcome": call.outcome.value,
            "summary": call.summary or "",
            "last_call_time": now_utc().strftime("%Y-%m-%d %H:%M"),
            "attempts": call.retry_count + 1,
        }
        
        # Add booking info if appointment was set
        if call.outcome == CallOutcome.APPOINTMENT_SET:
            sheet_updates["booked_date"] = call.metadata.get("booked_date", "")
            sheet_updates["booked_time"] = call.metadata.get("booked_time", "")
        
        sheets.update_row(
            spreadsheet_id=campaign.sheet_id if campaign else settings.google_sheets_spreadsheet_id,
            sheet_name="Sheet1",
            row_number=call.row_number,
            updates=sheet_updates,
        )
        logger.info(f"Updated sheet row {call.row_number} for call {call.id}")
        
    except Exception as e:
        logger.error(f"Failed to update sheet for call {call.id}: {e}")
        # Don't fail the webhook response - sheet update is best-effort
    
    logger.info(f"Processed webhook for call {call.id}: {call.status.value} / {call.outcome.value}")
    return {
        "status": "processed",
        "call_id": call.id,
        "outcome": call.outcome.value,
    }


@router.post("/elevenlabs/test")
async def test_webhook():
    """Test webhook endpoint for debugging."""
    return {"status": "ok", "message": "Webhook endpoint is reachable"}
