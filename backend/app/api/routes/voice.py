"""
Voice Calling API Routes
========================
Unified calling system that:
1. Fetches leads from Google Sheets
2. Initiates calls via ElevenLabs
3. Analyzes results with Claude
4. Updates results back to sheets
"""

from typing import Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException
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

class InitiateCallRequest(BaseModel):
    """Request to initiate a single call."""
    phone_number: str
    first_message: Optional[str] = None
    dynamic_variables: Optional[dict[str, str]] = None
    # Optional: Link to Google Sheet row
    spreadsheet_id: Optional[str] = None
    sheet_row_number: Optional[int] = None


class CallFromSheetRequest(BaseModel):
    """Request to call a lead from Google Sheets."""
    spreadsheet_id: str
    row_number: int
    phone_column: str  # Column header containing phone number
    sheet_name: Optional[str] = None
    # Column to update with result
    result_column: Optional[str] = None


class BatchCallFromSheetRequest(BaseModel):
    """Request to call multiple leads from Google Sheets."""
    spreadsheet_id: str
    phone_column: str
    sheet_name: Optional[str] = None
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
# Single Call Operations
# =============================================================================

@router.post("/call", response_model=CallResult)
async def initiate_call(req: InitiateCallRequest):
    """
    Initiate a single outbound call.
    
    Requires ELEVENLABS_AGENT_ID and ELEVENLABS_PHONE_NUMBER_ID to be configured.
    Can optionally link to a Google Sheet row for automatic result updates.
    """
    try:
        agent_id = settings.elevenlabs_agent_id
        phone_number_id = settings.elevenlabs_phone_number_id
        
        if not settings.mock_mode and (not agent_id or not phone_number_id):
            raise HTTPException(
                status_code=400,
                detail="ELEVENLABS_AGENT_ID and ELEVENLABS_PHONE_NUMBER_ID must be configured"
            )
        
        result = await elevenlabs.initiate_outbound_call(
            phone_number=req.phone_number,
            agent_id=agent_id or "mock-agent",
            phone_number_id=phone_number_id or "mock-phone",
            first_message=req.first_message,
            dynamic_variables=req.dynamic_variables,
        )
        
        return CallResult(
            call_id=result.get("call_id", ""),
            status=result.get("status", "unknown"),
            phone_number=req.phone_number,
            started_at=datetime.now(),
            metadata={
                "spreadsheet_id": req.spreadsheet_id,
                "sheet_row_number": req.sheet_row_number,
            } if req.spreadsheet_id else {},
        )
        
    except HTTPException:
        raise
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
        details = await elevenlabs.get_call_details(call_id)
        
        transcript = details.get("transcript")
        summary = None
        outcome = None
        sentiment = None
        
        # Run AI analysis if we have a transcript
        if analyze and transcript:
            ai_summary = claude.summarize_transcript(transcript)
            summary = ai_summary.brief
            outcome = ai_summary.outcome
            sentiment = ai_summary.customer_sentiment
        
        return CallStatusResponse(
            call_id=call_id,
            status=details.get("status", "unknown"),
            phone_number=details.get("phone_number", ""),
            duration_seconds=details.get("duration_seconds"),
            transcript=transcript,
            summary=summary,
            outcome=outcome,
            sentiment=sentiment,
            recording_url=details.get("recording_url"),
        )
        
    except Exception as e:
        logger.error(f"Failed to get call status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/call/{call_id}/transcript")
async def get_call_transcript(call_id: str):
    """Get the transcript of a call."""
    try:
        transcript = await elevenlabs.get_call_transcript(call_id)
        return {"success": True, "call_id": call_id, "transcript": transcript}
    except Exception as e:
        logger.error(f"Failed to get transcript: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Google Sheets Integration
# =============================================================================

@router.post("/call-from-sheet")
async def call_from_sheet(req: CallFromSheetRequest):
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
        
        # Prepare dynamic variables from row data
        dynamic_vars = {k: str(v) for k, v in row.data.items() if v is not None}
        
        agent_id = settings.elevenlabs_agent_id
        phone_number_id = settings.elevenlabs_phone_number_id
        
        if not settings.mock_mode and (not agent_id or not phone_number_id):
            raise HTTPException(
                status_code=400,
                detail="ELEVENLABS_AGENT_ID and ELEVENLABS_PHONE_NUMBER_ID must be configured"
            )
        
        # Initiate the call
        result = await elevenlabs.initiate_outbound_call(
            phone_number=str(phone),
            agent_id=agent_id or "mock-agent",
            phone_number_id=phone_number_id or "mock-phone",
            dynamic_variables=dynamic_vars,
        )
        
        call_id = result.get("call_id", "")
        
        # Update sheet that call was initiated
        if req.result_column and call_id:
            dynamic_sheets.update_row(
                spreadsheet_id=req.spreadsheet_id,
                row_number=req.row_number,
                updates={req.result_column: f"Calling... ({call_id})"},
                sheet_name=req.sheet_name,
            )
        
        return {
            "success": True,
            "call_id": call_id,
            "phone_number": str(phone),
            "row_data": row.data,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to call from sheet: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch-call")
async def batch_call_from_sheet(req: BatchCallFromSheetRequest):
    """
    Batch call multiple leads from a Google Sheet.
    
    1. Reads rows from the sheet
    2. Filters by criteria if provided
    3. Initiates calls for each row
    4. Updates result column if provided
    """
    try:
        # Read all data from sheet
        data_result = dynamic_sheets.read_data(
            spreadsheet_id=req.spreadsheet_id,
            sheet_name=req.sheet_name,
        )
        
        if not data_result or not data_result.rows:
            raise HTTPException(status_code=404, detail="No data found in sheet")
        
        # Filter rows
        rows_to_call = []
        for row in data_result.rows:
            # Skip rows before start_row
            if row.row_number < req.start_row:
                continue
            
            # Apply filter if specified
            if req.filter_column and req.filter_value:
                if row.data.get(req.filter_column) != req.filter_value:
                    continue
            
            # Check for phone number
            phone = row.data.get(req.phone_column)
            if not phone:
                continue
            
            rows_to_call.append(row)
            
            # Limit number of calls
            if len(rows_to_call) >= req.max_calls:
                break
        
        if not rows_to_call:
            return {
                "success": False,
                "error": "No rows found matching criteria",
                "calls_initiated": 0,
            }
        
        agent_id = settings.elevenlabs_agent_id
        phone_number_id = settings.elevenlabs_phone_number_id
        
        if not settings.mock_mode and (not agent_id or not phone_number_id):
            raise HTTPException(
                status_code=400,
                detail="ELEVENLABS_AGENT_ID and ELEVENLABS_PHONE_NUMBER_ID must be configured"
            )
        
        # Initiate calls
        results = []
        for row in rows_to_call:
            try:
                phone = str(row.data.get(req.phone_column))
                dynamic_vars = {k: str(v) for k, v in row.data.items() if v is not None}
                
                result = await elevenlabs.initiate_outbound_call(
                    phone_number=phone,
                    agent_id=agent_id or "mock-agent",
                    phone_number_id=phone_number_id or "mock-phone",
                    dynamic_variables=dynamic_vars,
                )
                
                call_id = result.get("call_id", "")
                
                # Update sheet with call ID
                if req.result_column and call_id:
                    dynamic_sheets.update_row(
                        spreadsheet_id=req.spreadsheet_id,
                        row_number=row.row_number,
                        updates={req.result_column: f"Calling... ({call_id})"},
                        sheet_name=req.sheet_name,
                    )
                
                results.append({
                    "row_number": row.row_number,
                    "phone_number": phone,
                    "call_id": call_id,
                    "success": True,
                })
                
            except Exception as e:
                results.append({
                    "row_number": row.row_number,
                    "phone_number": row.data.get(req.phone_column, ""),
                    "error": str(e),
                    "success": False,
                })
        
        successful = sum(1 for r in results if r.get("success"))
        
        return {
            "success": True,
            "calls_initiated": successful,
            "calls_failed": len(results) - successful,
            "results": results,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed batch call: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/update-sheet-result")
async def update_sheet_with_call_result(
    spreadsheet_id: str,
    row_number: int,
    call_id: str,
    result_column: str,
    sheet_name: Optional[str] = None,
):
    """
    Update a Google Sheet row with call results.
    
    Fetches call details, runs AI analysis, and updates the sheet.
    """
    try:
        # Get call details
        details = await elevenlabs.get_call_details(call_id)
        
        transcript = details.get("transcript")
        status = details.get("status", "unknown")
        duration = details.get("duration_seconds", 0)
        
        # Build result string
        result_parts = [f"Status: {status}", f"Duration: {duration}s"]
        
        # Add AI summary if transcript available
        if transcript:
            summary = claude.summarize_transcript(transcript)
            result_parts.append(f"Outcome: {summary.outcome}")
            result_parts.append(f"Sentiment: {summary.customer_sentiment}")
            result_parts.append(f"Summary: {summary.brief}")
        
        result_text = " | ".join(result_parts)
        
        # Update sheet
        dynamic_sheets.update_row(
            spreadsheet_id=spreadsheet_id,
            row_number=row_number,
            updates={result_column: result_text},
            sheet_name=sheet_name,
        )
        
        return {
            "success": True,
            "call_id": call_id,
            "result": result_text,
        }
        
    except Exception as e:
        logger.error(f"Failed to update sheet: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Health Check
# =============================================================================

@router.get("/health")
async def voice_health():
    """Check the health of voice calling services."""
    return {
        "status": "healthy",
        "elevenlabs_configured": bool(settings.elevenlabs_api_key),
        "agent_id_configured": bool(settings.elevenlabs_agent_id),
        "phone_number_id_configured": bool(settings.elevenlabs_phone_number_id),
        "mock_mode": settings.mock_mode,
    }
