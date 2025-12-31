"""
Dynamic Google Sheets API Routes
================================
Schema-less endpoints that work with ANY Google Sheet format.
"""

from typing import Optional, Any
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.services.dynamic_sheets import dynamic_sheets, SheetSchema, SheetData
from app.core.logging import logger

router = APIRouter(prefix="/api/sheets/v2", tags=["sheets-dynamic"])


# =============================================================================
# Request/Response Models
# =============================================================================

class ConnectSheetRequest(BaseModel):
    """Request to connect to a Google Sheet."""
    spreadsheet_id: str
    sheet_name: Optional[str] = None


class SheetSchemaResponse(BaseModel):
    """Response with detected sheet schema."""
    success: bool
    sheet_schema: Optional[SheetSchema] = None
    error: Optional[str] = None


class SheetDataResponse(BaseModel):
    """Response with sheet data."""
    success: bool
    sheet_schema: Optional[SheetSchema] = None
    rows: list[SheetData] = []
    total: int = 0
    error: Optional[str] = None


class UpdateRowRequest(BaseModel):
    """Request to update a row."""
    spreadsheet_id: str
    row_number: int
    updates: dict[str, Any]
    sheet_name: Optional[str] = None


class AppendRowRequest(BaseModel):
    """Request to append a row."""
    spreadsheet_id: str
    row_data: dict[str, Any]
    sheet_name: Optional[str] = None


class DeleteRowRequest(BaseModel):
    """Request to delete a row."""
    spreadsheet_id: str
    row_number: int
    sheet_name: Optional[str] = None


class SearchRequest(BaseModel):
    """Request to search rows."""
    spreadsheet_id: str
    column: str
    value: str
    exact_match: bool = False
    sheet_name: Optional[str] = None


class AddColumnRequest(BaseModel):
    """Request to add a new column."""
    spreadsheet_id: str
    column_name: str
    default_value: str = ""
    sheet_name: Optional[str] = None


# =============================================================================
# Endpoints
# =============================================================================

@router.post("/connect", response_model=SheetSchemaResponse)
async def connect_sheet(req: ConnectSheetRequest):
    """
    Connect to a Google Sheet and detect its schema.
    
    This endpoint:
    - Verifies access to the spreadsheet
    - Auto-detects all columns and their types
    - Returns the schema with sample data
    
    No hardcoded columns - works with ANY spreadsheet format!
    """
    try:
        schema = dynamic_sheets.detect_schema(
            spreadsheet_id=req.spreadsheet_id,
            sheet_name=req.sheet_name,
            force_refresh=True,
        )
        return SheetSchemaResponse(success=True, sheet_schema=schema)
    except Exception as e:
        logger.error(f"Failed to connect to sheet: {e}")
        return SheetSchemaResponse(success=False, error=str(e))


@router.get("/schema")
async def get_schema(
    spreadsheet_id: str,
    sheet_name: Optional[str] = None,
    refresh: bool = False,
):
    """Get the schema of a connected sheet."""
    try:
        schema = dynamic_sheets.detect_schema(
            spreadsheet_id=spreadsheet_id,
            sheet_name=sheet_name,
            force_refresh=refresh,
        )
        return {"success": True, "schema": schema.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/data", response_model=SheetDataResponse)
async def get_data(
    spreadsheet_id: str,
    sheet_name: Optional[str] = None,
    limit: Optional[int] = Query(default=100, le=1000),
    offset: int = Query(default=0, ge=0),
):
    """
    Get data from a sheet with pagination.
    
    Returns the schema along with the data rows.
    """
    try:
        schema, rows = dynamic_sheets.read_all_data(
            spreadsheet_id=spreadsheet_id,
            sheet_name=sheet_name,
            limit=limit,
            offset=offset,
        )
        return SheetDataResponse(
            success=True,
            sheet_schema=schema,
            rows=rows,
            total=schema.row_count,
        )
    except Exception as e:
        logger.error(f"Failed to get data: {e}")
        return SheetDataResponse(success=False, error=str(e))


@router.get("/row/{row_number}")
async def get_row(
    row_number: int,
    spreadsheet_id: str,
    sheet_name: Optional[str] = None,
):
    """Get a single row by row number."""
    try:
        row = dynamic_sheets.get_row(
            spreadsheet_id=spreadsheet_id,
            row_number=row_number,
            sheet_name=sheet_name,
        )
        if row:
            return {"success": True, "row": row.model_dump()}
        else:
            raise HTTPException(status_code=404, detail="Row not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/row")
async def update_row(req: UpdateRowRequest):
    """
    Update specific cells in a row.
    
    Only updates the columns specified in 'updates'.
    Column names must match the sheet headers.
    """
    try:
        success = dynamic_sheets.update_row(
            spreadsheet_id=req.spreadsheet_id,
            row_number=req.row_number,
            updates=req.updates,
            sheet_name=req.sheet_name,
        )
        return {"success": success}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/row")
async def append_row(req: AppendRowRequest):
    """
    Append a new row to the sheet.
    
    Column names in row_data must match sheet headers.
    """
    try:
        new_row_number = dynamic_sheets.append_row(
            spreadsheet_id=req.spreadsheet_id,
            row_data=req.row_data,
            sheet_name=req.sheet_name,
        )
        return {"success": new_row_number > 0, "row_number": new_row_number}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/row")
async def delete_row(req: DeleteRowRequest):
    """Delete a row from the sheet."""
    try:
        success = dynamic_sheets.delete_row(
            spreadsheet_id=req.spreadsheet_id,
            row_number=req.row_number,
            sheet_name=req.sheet_name,
        )
        return {"success": success}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/search")
async def search_rows(req: SearchRequest):
    """
    Search for rows matching a value in a specific column.
    
    Args:
        column: The column header to search in
        value: The value to search for
        exact_match: If true, requires exact match; otherwise uses contains
    """
    try:
        matches = dynamic_sheets.find_rows(
            spreadsheet_id=req.spreadsheet_id,
            column_header=req.column,
            value=req.value,
            sheet_name=req.sheet_name,
            exact_match=req.exact_match,
        )
        return {
            "success": True,
            "count": len(matches),
            "rows": [m.model_dump() for m in matches],
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/column/{column_name}/values")
async def get_column_values(
    column_name: str,
    spreadsheet_id: str,
    sheet_name: Optional[str] = None,
    unique: bool = False,
):
    """Get all values from a specific column."""
    try:
        values = dynamic_sheets.get_column_values(
            spreadsheet_id=spreadsheet_id,
            column_header=column_name,
            sheet_name=sheet_name,
            unique=unique,
        )
        return {"success": True, "values": values, "count": len(values)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/column")
async def add_column(req: AddColumnRequest):
    """Add a new column to the sheet."""
    try:
        success = dynamic_sheets.add_column(
            spreadsheet_id=req.spreadsheet_id,
            column_header=req.column_name,
            default_value=req.default_value,
            sheet_name=req.sheet_name,
        )
        return {"success": success}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/sheets")
async def list_sheets(spreadsheet_id: str):
    """List all sheets in a spreadsheet."""
    try:
        sheets = dynamic_sheets.list_sheets(spreadsheet_id)
        return {"success": True, "sheets": sheets}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# =============================================================================
# Utility Endpoints
# =============================================================================

@router.post("/validate-access")
async def validate_access(req: ConnectSheetRequest):
    """
    Validate that we can access a spreadsheet.
    
    Returns basic info without full data read.
    """
    try:
        sheets_list = dynamic_sheets.list_sheets(req.spreadsheet_id)
        if not sheets_list:
            return {"valid": False, "error": "Could not access spreadsheet"}
        
        return {
            "valid": True,
            "spreadsheet_id": req.spreadsheet_id,
            "sheets_count": len(sheets_list),
            "sheets": sheets_list,
        }
    except Exception as e:
        return {"valid": False, "error": str(e)}
