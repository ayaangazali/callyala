"""Google Sheets validation and utility endpoints."""

from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.config import settings
from app.services.sheets import sheets

router = APIRouter(prefix="/api/sheets", tags=["sheets"])


class ValidateSheetRequest(BaseModel):
    spreadsheet_id: Optional[str] = None
    range: Optional[str] = None


class ValidateSheetResponse(BaseModel):
    valid: bool
    spreadsheet_id: str
    title: str
    sheets: list[dict]
    row_count: int
    sample_rows: list[dict]
    missing_columns: list[str]
    errors: list[str]


REQUIRED_COLUMNS = ["phone"]
RECOMMENDED_COLUMNS = ["first_name", "last_name", "vehicle_interest"]


@router.post("/validate", response_model=ValidateSheetResponse)
async def validate_sheet(req: ValidateSheetRequest):
    """
    Validate access to a Google Sheet and check required columns.
    
    Returns sheet metadata, sample rows, and any missing columns.
    """
    spreadsheet_id = req.spreadsheet_id or settings.google_sheets_spreadsheet_id
    range_name = req.range or settings.google_sheets_range
    
    if not spreadsheet_id:
        raise HTTPException(
            status_code=400,
            detail="No spreadsheet_id provided and GOOGLE_SHEETS_SPREADSHEET_ID not set"
        )
    
    errors = []
    missing_columns = []
    
    try:
        # Get metadata
        metadata = sheets.get_sheet_metadata(spreadsheet_id)
        if not metadata:
            raise HTTPException(status_code=404, detail="Could not access spreadsheet")
        
        # Read rows
        rows = sheets.read_sheet(spreadsheet_id, range_name, use_cache=False)
        
        # Check for required columns by examining sample data
        if rows:
            sample = rows[0]
            for col in REQUIRED_COLUMNS:
                if not getattr(sample, col, None):
                    missing_columns.append(col)
            
            for col in RECOMMENDED_COLUMNS:
                if not getattr(sample, col, None):
                    errors.append(f"Recommended column '{col}' not found or empty")
        else:
            errors.append("No data rows found in sheet")
        
        # Prepare sample rows (first 5)
        sample_rows = [
            {
                "row_number": r.row_number,
                "full_name": r.full_name,
                "phone": r.phone,
                "vehicle_interest": r.vehicle_interest,
            }
            for r in rows[:5]
        ]
        
        return ValidateSheetResponse(
            valid=len(missing_columns) == 0 and len(rows) > 0,
            spreadsheet_id=spreadsheet_id,
            title=metadata.get("title", ""),
            sheets=metadata.get("sheets", []),
            row_count=len(rows),
            sample_rows=sample_rows,
            missing_columns=missing_columns,
            errors=errors,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to validate sheet: {str(e)}")


@router.get("/metadata")
async def get_sheet_metadata(spreadsheet_id: Optional[str] = None):
    """Get metadata for a Google Sheet."""
    spreadsheet_id = spreadsheet_id or settings.google_sheets_spreadsheet_id
    
    if not spreadsheet_id:
        raise HTTPException(
            status_code=400,
            detail="No spreadsheet_id provided"
        )
    
    try:
        metadata = sheets.get_sheet_metadata(spreadsheet_id)
        if not metadata:
            raise HTTPException(status_code=404, detail="Could not access spreadsheet")
        return metadata
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/preview")
async def preview_sheet(
    spreadsheet_id: Optional[str] = None,
    range: Optional[str] = None,
    limit: int = 10,
):
    """Preview rows from a Google Sheet."""
    spreadsheet_id = spreadsheet_id or settings.google_sheets_spreadsheet_id
    range_name = range or settings.google_sheets_range
    
    if not spreadsheet_id:
        raise HTTPException(status_code=400, detail="No spreadsheet_id provided")
    
    try:
        rows = sheets.read_sheet(spreadsheet_id, range_name, use_cache=False)
        return {
            "total": len(rows),
            "rows": [r.model_dump(mode="json") for r in rows[:limit]],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
