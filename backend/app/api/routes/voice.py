"""
Voice Calling API Routes
========================
Unified calling system that:
1. Fetches leads from Google Sheets
2. Initiates calls via ElevenLabs
3. Analyzes results with Claude
4. Updates results back to sheets
"""

from typing import Optional, Any
from datetime import datetime
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

from app.services.elevenlabs import elevenlabs
from app.services.dynamic_sheets import dynamic_sheets
from app.services.claude import claude
from app.core.config import settings
from app.core.logging import logger

router = APIRouter(prefix="/api/voice", tags=["voice-calling"])


# =============================================================================
# Request/Response Models
# =============================================================================

class AgentConfigRequest(BaseModel):
    """Configuration for the AI calling agent."""
    name: str = "Sarah"
    company_name: str = "Call Yala"
    first_message: str = "Hello! This is {agent_name} from {company_name}. How are you today?"
    system_prompt: Optional[str] = None
    voice_id: str = "21m00Tcm4TlvDq8ikWAM"  # Rachel
    language: str = "en"


class InitiateCallRequest(BaseModel):
    """Request to initiate a single call."""
    phone_number: str
    agent_id: Optional[str] = None
    agent_config: Optional[AgentConfigRequest] = None
    metadata: Optional[dict] = None
    # Optional: Link to Google Sheet row
    spreadsheet_id: Optional[str] = None
    sheet_row_number: Optional[int] = None


class CallFromSheetRequest(BaseModel):
    """Request to call a lead from Google Sheets."""
    spreadsheet_id: str
    row_number: int
    phone_column: str  # Column header containing phone number
    sheet_name: Optional[str] = None
    agent_id: Optional[str] = None
    # Column to update with result
    result_column: Optional[str] = None


class BatchCallFromSheetRequest(BaseModel):
    """Request to call multiple leads from Google Sheets."""
    spreadsheet_id: str
    phone_column: str
    sheet_name: Optional[str] = None
    agent_id: Optional[str] = None
    result_column: Optional[str] = None
    # Filters
    start_row: int = 2  # Skip header
    max_calls: int = 10
    # Optional: Only call rows where a column has a specific value
    filter_column: Optional[str] = None
    filter_value: Optional[str] = None


class CallResult(BaseModel):
    """Result of a call."""
    call_id: str
    status: str
    phone_number: str
    started_at: Optional[datetime] = None
    metadata: dict = {}


class CallStatusResponse(BaseModel):
    """Full status of a call."""
    call_id: str
    status: str
    phone_number: str
    duration_seconds: Optional[int] = None
    transcript: Optional[str] = None
    summary: Optional[str] = None
    outcome: Optional[str] = None
    sentiment: Optional[str] = None
    recording_url: Optional[str] = None


# =============================================================================
# Agent Management
# =============================================================================

@router.get("/voices")
async def list_voices():
    """Get available ElevenLabs voices for the agent."""
    try:
        voices = await elevenlabs.get_voices()
        return {"success": True, "voices": voices}
    except Exception as e:
        logger.error(f"Failed to get voices: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agent")
async def create_agent(config: AgentConfigRequest):
    """
    Create a new AI calling agent.
    
    Returns the agent_id to use for calls.
    """
    from app.services.elevenlabs import AgentConfig, VoiceConfig
    
    try:
        agent_config = AgentConfig(
            name=config.name,
            company_name=config.company_name,
            first_message=config.first_message,
            system_prompt=config.system_prompt or "",
            voice=VoiceConfig(voice_id=config.voice_id),
            language=config.language,
        )
        agent_id = await elevenlabs.create_agent(agent_config)
        return {"success": True, "agent_id": agent_id}
    except Exception as e:
        logger.error(f"Failed to create agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Single Call Operations
# =============================================================================

@router.post("/call", response_model=CallResult)
async def initiate_call(req: InitiateCallRequest):
    """
    Initiate a single outbound call.
    
    Can optionally link to a Google Sheet row for automatic result updates.
    """
    from app.services.elevenlabs import AgentConfig, VoiceConfig
    
    try:
        # Build agent config if provided
        agent_config = None
        if req.agent_config:
            agent_config = AgentConfig(
                name=req.agent_config.name,
                company_name=req.agent_config.company_name,
                first_message=req.agent_config.first_message,
                system_prompt=req.agent_config.system_prompt or "",
                voice=VoiceConfig(voice_id=req.agent_config.voice_id),
                language=req.agent_config.language,
            )
        
        # Add sheet info to metadata
        metadata = req.metadata or {}
        if req.spreadsheet_id and req.sheet_row_number:
            metadata["spreadsheet_id"] = req.spreadsheet_id
            metadata["sheet_row_number"] = req.sheet_row_number
        
        # Determine webhook URL for callbacks
        webhook_url = None
        if settings.app_env != "local":
            # In production, use the actual webhook URL
            webhook_url = f"https://your-domain.com/api/webhooks/elevenlabs"
        
        result = await elevenlabs.initiate_call(
            phone_number=req.phone_number,
            agent_id=req.agent_id or settings.elevenlabs_agent_id,
            agent_config=agent_config,
            metadata=metadata,
            webhook_url=webhook_url,
        )
        
        return CallResult(
            call_id=result.call_id,
            status=result.status.value,
            phone_number=result.phone_number,
            started_at=result.started_at,
            metadata=result.metadata,
        )
        
    except Exception as e:
        logger.error(f"Failed to initiate call: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/call/{call_id}", response_model=CallStatusResponse)
async def get_call_status(call_id: str, analyze: bool = True):
    """
    Get the status and details of a call.
    
    If analyze=True, also runs AI analysis on the transcript.
    """
    try:
        details = await elevenlabs.get_call_status(call_id)
        
        response = CallStatusResponse(
            call_id=details.call_id,
            status=details.status.value,
            phone_number=details.phone_number,
            duration_seconds=details.duration_seconds,
            transcript=details.transcript,
            recording_url=details.recording_url,
        )
        
        # Run AI analysis if we have a transcript
        if analyze and details.transcript:
            summary = claude.summarize_transcript(details.transcript)
            response.summary = summary.brief
            response.outcome = summary.outcome
            response.sentiment = summary.customer_sentiment
        
        return response
        
    except Exception as e:
        logger.error(f"Failed to get call status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/call/{call_id}/cancel")
async def cancel_call(call_id: str):
    """Cancel a queued or in-progress call."""
    try:
        success = await elevenlabs.cancel_call(call_id)
        return {"success": success}
    except Exception as e:
        logger.error(f"Failed to cancel call: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Google Sheets Integration
# =============================================================================

@router.post("/call-from-sheet")
async def call_from_sheet(req: CallFromSheetRequest, background_tasks: BackgroundTasks):
    """
    Call a lead directly from a Google Sheet row.
    
    1. Reads the row from the sheet
    2. Extracts the phone number
    3. Initiates the call
    4. Optionally updates a result column when done
    """
    try:
        # Get the row data
        row = dynamic_sheets.get_row(
            spreadsheet_id=req.spreadsheet_id,
            row_number=req.row_number,
            sheet_name=req.sheet_name,
        )
        
        if not row:
            raise HTTPException(status_code=404, detail=f"Row {req.row_number} not found")
        
        # Get phone number
        phone = row.data.get(req.phone_column)
        if not phone:
            raise HTTPException(
                status_code=400, 
                detail=f"No phone number in column '{req.phone_column}'"
            )
        
        # Prepare metadata with all row data
        metadata = {
            "spreadsheet_id": req.spreadsheet_id,
            "sheet_row_number": req.row_number,
            "result_column": req.result_column,
            "lead_data": row.data,
        }
        
        # Initiate the call
        result = await elevenlabs.initiate_call(
            phone_number=str(phone),
            agent_id=req.agent_id or settings.elevenlabs_agent_id,
            metadata=metadata,
        )
        
        # Update sheet that call was initiated
        if req.result_column:
            dynamic_sheets.update_row(
                spreadsheet_id=req.spreadsheet_id,
                row_number=req.row_number,
                updates={req.result_column: f"Calling... ({result.call_id})"},
                sheet_name=req.sheet_name,
            )
        
        return {
            "success": True,
            "call_id": result.call_id,
            "status": result.status.value,
            "phone_number": str(phone),
            "lead_data": row.data,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to call from sheet: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch-call-from-sheet")
async def batch_call_from_sheet(
    req: BatchCallFromSheetRequest,
    background_tasks: BackgroundTasks,
):
    """
    Call multiple leads from a Google Sheet.
    
    Reads rows from the sheet, filters if needed, and initiates calls.
    """
    try:
        # Get all data from the sheet
        schema, all_rows = dynamic_sheets.read_all_data(
            spreadsheet_id=req.spreadsheet_id,
            sheet_name=req.sheet_name,
        )
        
        # Filter rows
        rows_to_call = []
        for row in all_rows:
            if row.row_number < req.start_row:
                continue
            
            # Check filter if specified
            if req.filter_column and req.filter_value:
                cell_value = str(row.data.get(req.filter_column, "")).strip().lower()
                if cell_value != req.filter_value.lower():
                    continue
            
            # Check if has phone number
            phone = row.data.get(req.phone_column)
            if not phone:
                continue
            
            rows_to_call.append(row)
            
            if len(rows_to_call) >= req.max_calls:
                break
        
        if not rows_to_call:
            return {
                "success": False,
                "error": "No rows found matching criteria",
                "calls_initiated": 0,
            }
        
        # Initiate calls
        results = []
        for row in rows_to_call:
            phone = row.data.get(req.phone_column)
            
            try:
                metadata = {
                    "spreadsheet_id": req.spreadsheet_id,
                    "sheet_row_number": row.row_number,
                    "result_column": req.result_column,
                    "lead_data": row.data,
                }
                
                result = await elevenlabs.initiate_call(
                    phone_number=str(phone),
                    agent_id=req.agent_id or settings.elevenlabs_agent_id,
                    metadata=metadata,
                )
                
                # Update sheet
                if req.result_column:
                    dynamic_sheets.update_row(
                        spreadsheet_id=req.spreadsheet_id,
                        row_number=row.row_number,
                        updates={req.result_column: f"Calling... ({result.call_id})"},
                        sheet_name=req.sheet_name,
                    )
                
                results.append({
                    "row_number": row.row_number,
                    "call_id": result.call_id,
                    "status": result.status.value,
                    "phone": str(phone),
                })
                
            except Exception as e:
                logger.error(f"Failed to call row {row.row_number}: {e}")
                results.append({
                    "row_number": row.row_number,
                    "error": str(e),
                    "phone": str(phone),
                })
        
        successful = sum(1 for r in results if "call_id" in r)
        
        return {
            "success": True,
            "calls_initiated": successful,
            "calls_failed": len(results) - successful,
            "results": results,
        }
        
    except Exception as e:
        logger.error(f"Failed batch call: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Webhooks (for call completion callbacks)
# =============================================================================

@router.post("/webhook/call-complete")
async def handle_call_complete(payload: dict):
    """
    Handle webhook when a call completes.
    
    This is called by ElevenLabs when a call finishes.
    It:
    1. Gets the full transcript
    2. Analyzes it with Claude
    3. Updates the Google Sheet with results
    """
    try:
        call_id = payload.get("call_id")
        status = payload.get("status")
        transcript = payload.get("transcript")
        metadata = payload.get("metadata", {})
        
        logger.info(f"Call {call_id} completed with status {status}")
        
        # Analyze transcript
        summary = None
        if transcript:
            summary = claude.summarize_transcript(transcript, context=metadata.get("lead_data"))
        
        # Update Google Sheet if linked
        spreadsheet_id = metadata.get("spreadsheet_id")
        row_number = metadata.get("sheet_row_number")
        result_column = metadata.get("result_column")
        
        if spreadsheet_id and row_number and result_column:
            result_text = summary.outcome if summary else status
            if summary:
                result_text += f" | {summary.brief}"
            
            dynamic_sheets.update_row(
                spreadsheet_id=spreadsheet_id,
                row_number=row_number,
                updates={result_column: result_text},
            )
            logger.info(f"Updated sheet row {row_number} with result")
        
        return {
            "success": True,
            "call_id": call_id,
            "outcome": summary.outcome if summary else None,
            "sentiment": summary.customer_sentiment if summary else None,
        }
        
    except Exception as e:
        logger.error(f"Failed to handle webhook: {e}")
        return {"success": False, "error": str(e)}


# =============================================================================
# Usage & Health
# =============================================================================

@router.get("/usage")
async def get_usage():
    """Get ElevenLabs API usage statistics."""
    try:
        usage = await elevenlabs.get_usage()
        return {"success": True, "usage": usage}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/health")
async def voice_health():
    """Check health of voice calling service."""
    return {
        "status": "healthy",
        "elevenlabs_configured": bool(settings.elevenlabs_api_key),
        "agent_id_configured": bool(settings.elevenlabs_agent_id),
        "mock_mode": settings.mock_mode,
    }
