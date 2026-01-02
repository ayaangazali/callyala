"""
Webhook handler for ElevenLabs pickup reminder calls.
This is separate from the main webhooks.py to keep things clean.
"""

from typing import Any
from fastapi import APIRouter, HTTPException, Header, Request
from datetime import datetime

from app.core.config import settings
from app.core.logging import logger
from app.services.storage import storage
from app.services.webhook_verify import verify_elevenlabs_signature
from app.services.claude import claude

router = APIRouter(prefix="/api/webhooks/pickup", tags=["pickup-webhooks"])


@router.post("/elevenlabs")
async def elevenlabs_pickup_webhook(
    request: Request,
    x_elevenlabs_signature: str = Header(None, alias="X-ElevenLabs-Signature"),
):
    """
    Handle ElevenLabs webhooks specifically for pickup reminder calls.
    
    This webhook handler:
    1. Receives call events (started, ended, failed, etc.)
    2. Stores transcript and call details
    3. Uses Claude to analyze and extract pickup time
    4. Updates the local storage
    
    Events handled:
    - call.started / conversation.started
    - call.ended / conversation.ended / call.completed
    - call.failed / call.error
    - call.no_answer / no_answer
    - call.busy / busy
    
    NO MOCK DATA - all real API calls.
    """
    body = await request.body()
    
    # Verify signature (if secret is configured)
    if settings.elevenlabs_webhook_secret and x_elevenlabs_signature:
        if not verify_elevenlabs_signature(body, x_elevenlabs_signature):
            logger.warning("Pickup webhook signature verification failed")
            raise HTTPException(status_code=401, detail="Invalid signature")
    
    data = await request.json()
    logger.info(f"Received pickup webhook: {data.get('type', 'unknown')} for call {data.get('call_id')}")
    
    # Extract call ID
    call_id = data.get("call_id") or data.get("conversation_id")
    if not call_id:
        logger.warning("Webhook missing call_id")
        return {"status": "ignored", "reason": "no call_id"}
    
    # Check for duplicate (idempotency)
    webhook_id = f"pickup_{call_id}_{data.get('type', 'unknown')}"
    if storage.check_webhook_processed(webhook_id):
        logger.info(f"Duplicate pickup webhook for {call_id}")
        return {"status": "duplicate", "call_id": call_id}
    
    # Get stored call data
    stored_data = storage.get_call_simple(call_id)
    if not stored_data:
        logger.warning(f"Call {call_id} not found in storage, creating new record")
        stored_data = {
            "call_id": call_id,
            "created_at": datetime.now().isoformat(),
            "phone_number": "+96550525011",
        }
    
    # Update with webhook data based on event type
    event_type = data.get("type", "unknown")
    
    if event_type in ["call.started", "conversation.started"]:
        stored_data["status"] = "in-progress"
        stored_data["started_at"] = datetime.now().isoformat()
        logger.info(f"Call {call_id} started")
    
    elif event_type in ["call.ended", "conversation.ended", "call.completed"]:
        stored_data["status"] = "completed"
        stored_data["ended_at"] = datetime.now().isoformat()
        stored_data["completed_at"] = datetime.now().isoformat()
        
        # Extract call details from webhook payload
        transcript = data.get("transcript") or data.get("conversation_transcript", "")
        duration = data.get("duration_seconds") or data.get("call_duration", 0)
        recording_url = data.get("recording_url") or data.get("audio_url")
        
        stored_data["transcript"] = transcript
        stored_data["duration_seconds"] = duration
        stored_data["recording_url"] = recording_url
        
        # Run AI analysis if we have a transcript
        if transcript:
            try:
                logger.info(f"Running AI analysis on call {call_id}")
                ai_summary = claude.summarize_transcript(transcript)
                
                stored_data["summary"] = ai_summary.brief
                stored_data["sentiment"] = ai_summary.customer_sentiment
                stored_data["key_points"] = ai_summary.key_points
                stored_data["action_items"] = ai_summary.action_items
                stored_data["outcome"] = ai_summary.outcome
                
                # Extract pickup time from action items
                pickup_time = None
                for action in ai_summary.action_items:
                    if "pickup" in action.lower() or "pick up" in action.lower():
                        pickup_time = action
                        break
                
                stored_data["pickup_time_scheduled"] = pickup_time
                
                logger.info(
                    f"AI Analysis complete for {call_id}: "
                    f"outcome={ai_summary.outcome}, sentiment={ai_summary.customer_sentiment}"
                )
                
            except Exception as e:
                logger.error(f"AI analysis failed for call {call_id}: {e}")
                stored_data["analysis_error"] = str(e)
        
        logger.info(f"Call {call_id} completed - duration: {duration}s")
    
    elif event_type in ["call.failed", "call.error"]:
        stored_data["status"] = "failed"
        stored_data["error"] = data.get("error") or data.get("reason", "Unknown error")
        stored_data["ended_at"] = datetime.now().isoformat()
        logger.warning(f"Call {call_id} failed: {stored_data.get('error')}")
    
    elif event_type in ["call.no_answer", "no_answer"]:
        stored_data["status"] = "no-answer"
        stored_data["ended_at"] = datetime.now().isoformat()
        logger.info(f"Call {call_id} - no answer")
    
    elif event_type in ["call.busy", "busy"]:
        stored_data["status"] = "busy"
        stored_data["ended_at"] = datetime.now().isoformat()
        logger.info(f"Call {call_id} - busy")
    
    elif event_type in ["call.voicemail", "voicemail"]:
        stored_data["status"] = "voicemail"
        stored_data["ended_at"] = datetime.now().isoformat()
        logger.info(f"Call {call_id} - voicemail")
    
    # Save updated data
    storage.save_call(call_id, stored_data)
    storage.mark_webhook_processed(webhook_id)
    
    logger.info(f"Processed pickup webhook for {call_id}: status={stored_data.get('status')}")
    
    return {
        "status": "processed",
        "call_id": call_id,
        "event_type": event_type,
        "call_status": stored_data.get("status"),
        "has_transcript": bool(stored_data.get("transcript")),
        "has_analysis": bool(stored_data.get("summary")),
        "pickup_time": stored_data.get("pickup_time_scheduled"),
    }


@router.get("/test")
async def test_pickup_webhook():
    """Test endpoint to verify pickup webhook is accessible."""
    return {
        "status": "ok",
        "message": "Pickup webhook endpoint is alive",
        "webhook_url": "/api/webhooks/pickup/elevenlabs",
        "instructions": "Configure this URL in your ElevenLabs agent settings",
    }
