"""
Car Pickup Reminder - Main Calling Endpoint
============================================
Make real outbound calls to customers for car pickup reminders.
NO MOCK DATA - Uses real Anthropic and ElevenLabs APIs.
"""

from typing import Optional, Any
from datetime import datetime
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

from app.services.elevenlabs import elevenlabs
from app.services.claude import claude
from app.services.storage import storage
from app.core.config import settings
from app.core.logging import logger

router = APIRouter(prefix="/api/pickup", tags=["car-pickup-reminders"])


# =============================================================================
# Request/Response Models
# =============================================================================

class PickupReminderRequest(BaseModel):
    """Request to call a customer about car pickup."""
    customer_name: str
    vehicle_make: str = "Toyota"
    vehicle_model: str = "Camry"
    service_type: str = "regular maintenance"
    service_notes: Optional[str] = "Service completed successfully"
    # Phone number - will be HARDCODED to demo number in actual call
    customer_phone_display: Optional[str] = None  # For display only


class PickupReminderResponse(BaseModel):
    """Response from initiating a pickup reminder call."""
    success: bool
    call_id: str
    message: str
    actual_phone_called: str  # Always +96550525011 for demo
    customer_name: str
    vehicle_info: str
    started_at: datetime


class CallStatusResponse(BaseModel):
    """Status of a pickup reminder call."""
    call_id: str
    status: str  # queued, ringing, in-progress, completed, failed, no-answer, busy
    customer_name: str
    vehicle_info: str
    phone_number: str
    duration_seconds: Optional[int] = None
    pickup_time_scheduled: Optional[str] = None  # Extracted from transcript
    transcript: Optional[str] = None
    summary: Optional[str] = None
    sentiment: Optional[str] = None
    recording_url: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None


# =============================================================================
# Main Endpoint: Make Pickup Reminder Call
# =============================================================================

@router.post("/call", response_model=PickupReminderResponse)
async def call_for_pickup_reminder(
    req: PickupReminderRequest,
    background_tasks: BackgroundTasks,
):
    """
    Call a customer to schedule car pickup after service completion.
    
    DEMO MODE: All calls go to +96550525011 regardless of customer info.
    
    The AI agent will:
    1. Greet the customer
    2. Inform them their car is ready
    3. Ask when they can pick it up
    4. Answer any questions about the service
    5. Confirm the pickup time
    6. Store the transcript and results
    
    Returns:
        Call ID and status - use GET /pickup/status/{call_id} to check progress
    """
    try:
        # Validate API keys are configured
        if not settings.elevenlabs_api_key:
            raise HTTPException(
                status_code=500,
                detail="ELEVENLABS_API_KEY not configured. Add it to your .env file."
            )
        
        if not settings.elevenlabs_agent_id:
            raise HTTPException(
                status_code=500,
                detail="ELEVENLABS_AGENT_ID not configured. Set up your agent first."
            )
        
        if not settings.elevenlabs_phone_number_id:
            raise HTTPException(
                status_code=500,
                detail="ELEVENLABS_PHONE_NUMBER_ID not configured. Add a phone number."
            )
        
        # HARDCODED DEMO NUMBER - Always call this number
        demo_target = "+96550525011"
        
        logger.info(f"Initiating pickup reminder call for {req.customer_name} - {req.vehicle_make} {req.vehicle_model}")
        logger.info(f"DEMO MODE: Calling {demo_target} (hardcoded for demo)")
        
        # Prepare dynamic variables for the AI agent
        dynamic_variables = {
            "customer_name": req.customer_name,
            "vehicle_make": req.vehicle_make,
            "vehicle_model": req.vehicle_model,
            "service_type": req.service_type,
            "service_notes": req.service_notes or "Service completed successfully",
        }
        
        # First message to start the conversation
        first_message = (
            f"Hello, is this {req.customer_name}? "
            f"This is a call from your car service center regarding your "
            f"{req.vehicle_make} {req.vehicle_model}."
        )
        
        # Initiate the actual call via ElevenLabs
        result = await elevenlabs.initiate_outbound_call(
            phone_number=demo_target,  # HARDCODED
            agent_id=settings.elevenlabs_agent_id,
            phone_number_id=settings.elevenlabs_phone_number_id,
            first_message=first_message,
            dynamic_variables=dynamic_variables,
        )
        
        call_id = result.get("call_id")
        
        # Store call metadata locally
        call_data = {
            "call_id": call_id,
            "customer_name": req.customer_name,
            "vehicle_make": req.vehicle_make,
            "vehicle_model": req.vehicle_model,
            "service_type": req.service_type,
            "service_notes": req.service_notes,
            "phone_number": demo_target,
            "status": result.get("status", "queued"),
            "created_at": datetime.now().isoformat(),
            "dynamic_variables": dynamic_variables,
        }
        
        storage.save_call(call_id, call_data)
        
        logger.info(f"Call initiated successfully: {call_id}")
        
        vehicle_info = f"{req.vehicle_make} {req.vehicle_model}"
        
        return PickupReminderResponse(
            success=True,
            call_id=call_id,
            message=f"Call initiated to {demo_target} for {req.customer_name}",
            actual_phone_called=demo_target,
            customer_name=req.customer_name,
            vehicle_info=vehicle_info,
            started_at=datetime.now(),
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to initiate pickup reminder call: {e}")
        raise HTTPException(status_code=500, detail=f"Call failed: {str(e)}")


# =============================================================================
# Check Call Status
# =============================================================================

@router.get("/status/{call_id}", response_model=CallStatusResponse)
async def get_pickup_call_status(call_id: str, analyze: bool = True):
    """
    Get the status of a pickup reminder call.
    
    If analyze=True (default), also runs AI analysis to:
    - Summarize the conversation
    - Extract pickup time scheduled
    - Analyze customer sentiment
    - Extract any concerns or questions
    
    Args:
        call_id: The call ID returned from /pickup/call
        analyze: Whether to run AI analysis on the transcript
    """
    try:
        # Get stored call metadata
        stored_data = storage.get_call_simple(call_id)
        if not stored_data:
            raise HTTPException(status_code=404, detail="Call not found")
        
        customer_name = stored_data.get("customer_name", "Unknown")
        vehicle_info = f"{stored_data.get('vehicle_make', '')} {stored_data.get('vehicle_model', '')}"
        
        # Get live status from ElevenLabs
        try:
            details = await elevenlabs.get_call_details(call_id)
            status = details.get("status", "unknown")
            duration = details.get("duration_seconds")
            transcript = details.get("transcript")
            recording_url = details.get("recording_url")
            completed_at = details.get("completed_at")
            
            # Update stored data with latest info
            stored_data.update({
                "status": status,
                "duration_seconds": duration,
                "transcript": transcript,
                "recording_url": recording_url,
                "completed_at": completed_at,
            })
            
        except Exception as e:
            logger.warning(f"Could not fetch live call details: {e}")
            # Use stored data
            status = stored_data.get("status", "unknown")
            duration = stored_data.get("duration_seconds")
            transcript = stored_data.get("transcript")
            recording_url = stored_data.get("recording_url")
            completed_at = stored_data.get("completed_at")
        
        # AI Analysis
        summary = None
        sentiment = None
        pickup_time = None
        
        if analyze and transcript:
            try:
                logger.info(f"Running AI analysis on call {call_id}")
                
                # Use Claude to analyze the transcript
                ai_summary = claude.summarize_transcript(transcript)
                summary = ai_summary.brief
                sentiment = ai_summary.customer_sentiment
                
                # Extract pickup time from action items or key points
                for action in ai_summary.action_items:
                    if "pickup" in action.lower() or "pick up" in action.lower():
                        pickup_time = action
                        break
                
                # Store analysis results
                stored_data.update({
                    "summary": summary,
                    "sentiment": sentiment,
                    "pickup_time_scheduled": pickup_time,
                })
                
                storage.save_call(call_id, stored_data)
                
            except Exception as e:
                logger.error(f"AI analysis failed: {e}")
                # Continue without analysis
        
        return CallStatusResponse(
            call_id=call_id,
            status=status,
            customer_name=customer_name,
            vehicle_info=vehicle_info,
            phone_number=stored_data.get("phone_number", "+96550525011"),
            duration_seconds=duration,
            pickup_time_scheduled=pickup_time,
            transcript=transcript,
            summary=summary,
            sentiment=sentiment,
            recording_url=recording_url,
            created_at=datetime.fromisoformat(stored_data.get("created_at", datetime.now().isoformat())),
            completed_at=datetime.fromisoformat(completed_at) if completed_at else None,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get call status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# List All Calls
# =============================================================================

@router.get("/calls")
async def list_pickup_calls(limit: int = 50):
    """
    List all pickup reminder calls.
    
    Returns the most recent calls with their status and summary info.
    """
    try:
        calls = storage.list_calls(limit=limit)
        return {
            "success": True,
            "count": len(calls),
            "calls": calls,
        }
    except Exception as e:
        logger.error(f"Failed to list calls: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Get Transcript Only
# =============================================================================

@router.get("/transcript/{call_id}")
async def get_pickup_call_transcript(call_id: str):
    """Get just the transcript of a call."""
    try:
        stored_data = storage.get_call_simple(call_id)
        if not stored_data:
            raise HTTPException(status_code=404, detail="Call not found")
        
        transcript = stored_data.get("transcript")
        
        if not transcript:
            # Try to fetch from ElevenLabs
            try:
                transcript = await elevenlabs.get_call_transcript(call_id)
                # Update storage
                stored_data["transcript"] = transcript
                storage.save_call(call_id, stored_data)
            except Exception as e:
                logger.warning(f"Could not fetch transcript: {e}")
        
        return {
            "success": True,
            "call_id": call_id,
            "transcript": transcript or "Transcript not available yet",
            "customer_name": stored_data.get("customer_name"),
            "vehicle_info": f"{stored_data.get('vehicle_make', '')} {stored_data.get('vehicle_model', '')}",
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get transcript: {e}")
        raise HTTPException(status_code=500, detail=str(e))
