"""Google Sheets integration service."""

from typing import Any, Optional
import json

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.core.config import settings
from app.core.files import atomic_write_json, read_json
from app.core.logging import logger
from app.core.time import now_utc
from app.models import SheetRow


# Expected column headers (case-insensitive matching)
COLUMN_MAPPINGS = {
    "first_name": ["first name", "firstname", "first", "name"],
    "last_name": ["last name", "lastname", "last", "surname"],
    "phone": ["phone", "phone number", "phonenumber", "mobile", "cell", "telephone"],
    "email": ["email", "e-mail", "email address"],
    "vehicle_interest": ["vehicle", "vehicle interest", "car", "model", "vehicle_interest"],
    "notes": ["notes", "note", "comments", "comment"],
}


class SheetsService:
    """Google Sheets API client."""

    def __init__(self):
        self._service = None

    def _get_service(self):
        """Get or create Sheets API service."""
        if self._service is None:
            if settings.mock_mode:
                logger.info("MOCK_MODE: Sheets service not initialized")
                return None
            
            if not settings.google_service_account_json_path.exists():
                raise ValueError(
                    f"Service account JSON not found: {settings.google_service_account_json_path}"
                )
            
            creds = service_account.Credentials.from_service_account_file(
                str(settings.google_service_account_json_path),
                scopes=["https://www.googleapis.com/auth/spreadsheets"],
            )
            self._service = build("sheets", "v4", credentials=creds)
        
        return self._service

    def _match_column(self, header: str) -> Optional[str]:
        """Match a header to a known field name."""
        header_lower = header.lower().strip()
        for field, aliases in COLUMN_MAPPINGS.items():
            if header_lower in aliases:
                return field
        return None

    def read_sheet(
        self,
        spreadsheet_id: str,
        range_name: str,
        use_cache: bool = True,
        cache_ttl_seconds: int = 300,
    ) -> list[SheetRow]:
        """Read rows from a Google Sheet."""
        
        # Check cache first
        if use_cache:
            cache = read_json(settings.sheet_cache_file, default={})
            cache_key = f"{spreadsheet_id}:{range_name}"
            if cache_key in cache:
                cached = cache[cache_key]
                cached_at = cached.get("cached_at", "")
                # Simple TTL check
                if cached_at:
                    from datetime import datetime
                    try:
                        cache_time = datetime.fromisoformat(cached_at.replace("Z", "+00:00"))
                        age = (now_utc() - cache_time).total_seconds()
                        if age < cache_ttl_seconds:
                            logger.debug(f"Using cached sheet data ({age:.0f}s old)")
                            return [SheetRow(**r) for r in cached.get("rows", [])]
                    except Exception:
                        pass

        # Mock mode - return sample data
        if settings.mock_mode:
            logger.info("MOCK_MODE: Returning sample sheet data")
            return [
                SheetRow(
                    row_number=2,
                    first_name="Ahmed",
                    last_name="Al-Sabah",
                    phone="+96512345678",
                    email="ahmed@example.com",
                    vehicle_interest="2024 Toyota Camry",
                ),
                SheetRow(
                    row_number=3,
                    first_name="Fatima",
                    last_name="Al-Ahmad",
                    phone="+96598765432",
                    email="fatima@example.com",
                    vehicle_interest="2024 Honda Accord",
                ),
            ]

        # Fetch from Google Sheets
        service = self._get_service()
        if not service:
            return []

        try:
            result = (
                service.spreadsheets()
                .values()
                .get(spreadsheetId=spreadsheet_id, range=range_name)
                .execute()
            )
            values = result.get("values", [])
            
            if not values:
                logger.warning(f"No data found in sheet {spreadsheet_id}")
                return []

            # First row is headers
            headers = values[0]
            rows = []

            for row_idx, row in enumerate(values[1:], start=2):
                # Build row data
                row_data = {"row_number": row_idx, "extra_fields": {}}
                
                for col_idx, value in enumerate(row):
                    if col_idx >= len(headers):
                        continue
                    
                    header = headers[col_idx]
                    field = self._match_column(header)
                    
                    if field:
                        row_data[field] = value
                    else:
                        row_data["extra_fields"][header] = value

                # Skip rows without phone
                if not row_data.get("phone"):
                    continue

                try:
                    rows.append(SheetRow(**row_data))
                except Exception as e:
                    logger.warning(f"Skipping invalid row {row_idx}: {e}")

            # Update cache
            cache = read_json(settings.sheet_cache_file, default={})
            cache[f"{spreadsheet_id}:{range_name}"] = {
                "rows": [r.model_dump(mode="json") for r in rows],
                "cached_at": now_utc().isoformat(),
            }
            atomic_write_json(settings.sheet_cache_file, cache)

            logger.info(f"Read {len(rows)} rows from sheet {spreadsheet_id}")
            return rows

        except HttpError as e:
            logger.error(f"Google Sheets API error: {e}")
            raise

    def write_result(
        self,
        spreadsheet_id: str,
        row_number: int,
        result_column: str,
        value: str,
    ) -> bool:
        """Write a result back to the sheet."""
        if settings.mock_mode:
            logger.info(f"MOCK_MODE: Would write '{value}' to row {row_number}")
            return True

        service = self._get_service()
        if not service:
            return False

        try:
            # Construct the range (e.g., "Sheet1!G2")
            range_name = f"{result_column}{row_number}"
            
            body = {"values": [[value]]}
            
            service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption="RAW",
                body=body,
            ).execute()
            
            logger.debug(f"Wrote result to {range_name}")
            return True

        except HttpError as e:
            logger.error(f"Failed to write to sheet: {e}")
            return False

    def get_sheet_metadata(self, spreadsheet_id: str) -> dict[str, Any]:
        """Get sheet metadata (title, sheets list, etc.)."""
        if settings.mock_mode:
            return {
                "title": "Mock Spreadsheet",
                "sheets": [{"title": "Sheet1"}],
            }

        service = self._get_service()
        if not service:
            return {}

        try:
            result = (
                service.spreadsheets()
                .get(spreadsheetId=spreadsheet_id, fields="properties.title,sheets.properties.title")
                .execute()
            )
            
            return {
                "title": result.get("properties", {}).get("title", ""),
                "sheets": [
                    {"title": s.get("properties", {}).get("title", "")}
                    for s in result.get("sheets", [])
                ],
            }

        except HttpError as e:
            logger.error(f"Failed to get sheet metadata: {e}")
            return {}

    def ensure_columns(
        self,
        spreadsheet_id: str,
        sheet_name: str,
        required_columns: list[str],
    ) -> bool:
        """Ensure required columns exist in the sheet header."""
        if settings.mock_mode:
            logger.info(f"MOCK_MODE: Would ensure columns {required_columns}")
            return True

        service = self._get_service()
        if not service:
            return False

        try:
            # Read current headers
            result = (
                service.spreadsheets()
                .values()
                .get(spreadsheetId=spreadsheet_id, range=f"{sheet_name}!1:1")
                .execute()
            )
            current_headers = result.get("values", [[]])[0]
            current_headers_lower = [h.lower() for h in current_headers]

            # Find missing columns
            missing = []
            for col in required_columns:
                if col.lower() not in current_headers_lower:
                    missing.append(col)

            if not missing:
                return True

            # Append missing columns to header row
            start_col = len(current_headers)
            end_col = start_col + len(missing)
            col_letter_start = chr(ord('A') + start_col)
            col_letter_end = chr(ord('A') + end_col - 1)
            
            range_name = f"{sheet_name}!{col_letter_start}1:{col_letter_end}1"
            
            service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption="RAW",
                body={"values": [missing]},
            ).execute()

            logger.info(f"Added columns {missing} to sheet {spreadsheet_id}")
            return True

        except HttpError as e:
            logger.error(f"Failed to ensure columns: {e}")
            return False

    def update_row(
        self,
        spreadsheet_id: str,
        sheet_name: str,
        row_number: int,
        updates: dict[str, Any],
    ) -> bool:
        """Update specific columns in a row."""
        if settings.mock_mode:
            logger.info(f"MOCK_MODE: Would update row {row_number} with {updates}")
            return True

        service = self._get_service()
        if not service:
            return False

        try:
            # Get headers to find column indices
            result = (
                service.spreadsheets()
                .values()
                .get(spreadsheetId=spreadsheet_id, range=f"{sheet_name}!1:1")
                .execute()
            )
            headers = result.get("values", [[]])[0]
            headers_lower = [h.lower() for h in headers]

            # Build batch update requests
            data = []
            for col_name, value in updates.items():
                col_name_lower = col_name.lower()
                if col_name_lower in headers_lower:
                    col_idx = headers_lower.index(col_name_lower)
                    col_letter = chr(ord('A') + col_idx)
                    range_name = f"{sheet_name}!{col_letter}{row_number}"
                    data.append({
                        "range": range_name,
                        "values": [[str(value) if value is not None else ""]],
                    })

            if data:
                service.spreadsheets().values().batchUpdate(
                    spreadsheetId=spreadsheet_id,
                    body={"valueInputOption": "RAW", "data": data},
                ).execute()
                logger.debug(f"Updated row {row_number} in sheet {spreadsheet_id}")

            return True

        except HttpError as e:
            logger.error(f"Failed to update row: {e}")
            return False

    def batch_update_rows(
        self,
        spreadsheet_id: str,
        sheet_name: str,
        updates: list[dict[str, Any]],
    ) -> bool:
        """
        Batch update multiple rows.
        
        Args:
            updates: List of dicts with 'row_number' and column->value pairs
        """
        if settings.mock_mode:
            logger.info(f"MOCK_MODE: Would batch update {len(updates)} rows")
            return True

        service = self._get_service()
        if not service:
            return False

        try:
            # Get headers
            result = (
                service.spreadsheets()
                .values()
                .get(spreadsheetId=spreadsheet_id, range=f"{sheet_name}!1:1")
                .execute()
            )
            headers = result.get("values", [[]])[0]
            headers_lower = [h.lower() for h in headers]

            # Build all update data
            data = []
            for update in updates:
                row_number = update.get("row_number")
                if not row_number:
                    continue

                for col_name, value in update.items():
                    if col_name == "row_number":
                        continue
                    col_name_lower = col_name.lower()
                    if col_name_lower in headers_lower:
                        col_idx = headers_lower.index(col_name_lower)
                        col_letter = chr(ord('A') + col_idx)
                        range_name = f"{sheet_name}!{col_letter}{row_number}"
                        data.append({
                            "range": range_name,
                            "values": [[str(value) if value is not None else ""]],
                        })

            if data:
                service.spreadsheets().values().batchUpdate(
                    spreadsheetId=spreadsheet_id,
                    body={"valueInputOption": "RAW", "data": data},
                ).execute()
                logger.info(f"Batch updated {len(updates)} rows in sheet {spreadsheet_id}")

            return True

        except HttpError as e:
            logger.error(f"Failed to batch update rows: {e}")
            return False

# Singleton instance
sheets = SheetsService()
