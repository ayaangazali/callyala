"""
Dynamic Google Sheets Integration Service
=========================================
Schema-less integration that works with ANY Google Sheet format.
No hardcoded columns - automatically detects and adapts to any structure.
"""

from typing import Any, Optional
from datetime import datetime
import json
import re

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pydantic import BaseModel

from app.core.config import settings
from app.core.logging import logger


class SheetColumn(BaseModel):
    """Represents a column in a sheet."""
    index: int
    header: str
    letter: str  # A, B, C, etc.
    sample_values: list[str] = []
    detected_type: str = "string"  # string, phone, email, number, date, url


class SheetSchema(BaseModel):
    """Dynamically detected schema of a sheet."""
    spreadsheet_id: str
    spreadsheet_title: str
    sheet_name: str
    sheet_id: int
    columns: list[SheetColumn]
    row_count: int
    has_header: bool = True


class SheetData(BaseModel):
    """Generic data from a sheet - no fixed structure."""
    row_number: int
    data: dict[str, Any]  # column_header -> value


class DynamicSheetsService:
    """
    Dynamic Google Sheets service that works with ANY spreadsheet format.
    
    Features:
    - Auto-detect schema from any sheet
    - No hardcoded columns
    - Smart column type detection (phone, email, etc.)
    - CRUD operations on any sheet
    - Batch operations for efficiency
    """

    def __init__(self):
        self._service = None
        self._schema_cache: dict[str, SheetSchema] = {}

    def _get_service(self):
        """Get or create Sheets API service."""
        if self._service is None:
            if settings.mock_mode:
                logger.info("MOCK_MODE: Using mock sheets service")
                return None
            
            # Check for service account JSON
            if not settings.google_service_account_json_path.exists():
                raise ValueError(
                    f"Google service account JSON not found at: {settings.google_service_account_json_path}. "
                    "Please place your service account credentials file there."
                )
            
            creds = service_account.Credentials.from_service_account_file(
                str(settings.google_service_account_json_path),
                scopes=["https://www.googleapis.com/auth/spreadsheets"],
            )
            self._service = build("sheets", "v4", credentials=creds)
        
        return self._service

    @staticmethod
    def _col_index_to_letter(index: int) -> str:
        """Convert 0-based column index to letter (0 -> A, 1 -> B, 26 -> AA)."""
        result = ""
        while index >= 0:
            result = chr(index % 26 + ord('A')) + result
            index = index // 26 - 1
        return result

    @staticmethod
    def _detect_column_type(values: list[str]) -> str:
        """Detect the data type of a column based on sample values."""
        if not values:
            return "string"
        
        # Filter empty values
        non_empty = [v for v in values if v and str(v).strip()]
        if not non_empty:
            return "string"
        
        # Check patterns
        phone_pattern = re.compile(r'^[\+]?[(]?[0-9]{1,4}[)]?[-\s\./0-9]{7,}$')
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        url_pattern = re.compile(r'^https?://|www\.')
        date_pattern = re.compile(r'^\d{1,4}[-/]\d{1,2}[-/]\d{1,4}$')
        
        type_counts = {"phone": 0, "email": 0, "url": 0, "date": 0, "number": 0, "string": 0}
        
        for val in non_empty[:10]:  # Check first 10 values
            val_str = str(val).strip()
            
            if phone_pattern.match(val_str.replace(" ", "")):
                type_counts["phone"] += 1
            elif email_pattern.match(val_str):
                type_counts["email"] += 1
            elif url_pattern.match(val_str):
                type_counts["url"] += 1
            elif date_pattern.match(val_str):
                type_counts["date"] += 1
            else:
                try:
                    float(val_str.replace(",", ""))
                    type_counts["number"] += 1
                except ValueError:
                    type_counts["string"] += 1
        
        # Return the most common type
        return max(type_counts, key=type_counts.get)

    def detect_schema(
        self,
        spreadsheet_id: str,
        sheet_name: Optional[str] = None,
        force_refresh: bool = False,
    ) -> SheetSchema:
        """
        Detect the schema of a Google Sheet automatically.
        
        Args:
            spreadsheet_id: The Google Sheet ID
            sheet_name: Specific sheet name (uses first sheet if not provided)
            force_refresh: Force re-detection even if cached
        
        Returns:
            SheetSchema with all detected columns and types
        """
        cache_key = f"{spreadsheet_id}:{sheet_name or 'default'}"
        
        if not force_refresh and cache_key in self._schema_cache:
            return self._schema_cache[cache_key]
        
        # Mock mode
        if settings.mock_mode:
            return SheetSchema(
                spreadsheet_id=spreadsheet_id,
                spreadsheet_title="Mock Spreadsheet",
                sheet_name=sheet_name or "Sheet1",
                sheet_id=0,
                columns=[
                    SheetColumn(index=0, header="Name", letter="A", detected_type="string"),
                    SheetColumn(index=1, header="Phone", letter="B", detected_type="phone"),
                    SheetColumn(index=2, header="Email", letter="C", detected_type="email"),
                    SheetColumn(index=3, header="Notes", letter="D", detected_type="string"),
                ],
                row_count=10,
                has_header=True,
            )
        
        service = self._get_service()
        if not service:
            raise ValueError("Sheets service not available")
        
        try:
            # Get spreadsheet metadata
            spreadsheet = service.spreadsheets().get(
                spreadsheetId=spreadsheet_id,
                fields="properties.title,sheets(properties(sheetId,title,gridProperties))"
            ).execute()
            
            spreadsheet_title = spreadsheet.get("properties", {}).get("title", "")
            sheets_list = spreadsheet.get("sheets", [])
            
            if not sheets_list:
                raise ValueError("No sheets found in spreadsheet")
            
            # Find the target sheet
            target_sheet = None
            if sheet_name:
                for s in sheets_list:
                    if s.get("properties", {}).get("title") == sheet_name:
                        target_sheet = s
                        break
                if not target_sheet:
                    raise ValueError(f"Sheet '{sheet_name}' not found")
            else:
                target_sheet = sheets_list[0]
            
            sheet_props = target_sheet.get("properties", {})
            actual_sheet_name = sheet_props.get("title", "Sheet1")
            sheet_id = sheet_props.get("sheetId", 0)
            grid_props = sheet_props.get("gridProperties", {})
            row_count = grid_props.get("rowCount", 0)
            col_count = grid_props.get("columnCount", 0)
            
            # Read first few rows to detect schema
            range_name = f"'{actual_sheet_name}'!A1:{self._col_index_to_letter(col_count - 1)}20"
            result = service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get("values", [])
            if not values:
                return SheetSchema(
                    spreadsheet_id=spreadsheet_id,
                    spreadsheet_title=spreadsheet_title,
                    sheet_name=actual_sheet_name,
                    sheet_id=sheet_id,
                    columns=[],
                    row_count=0,
                    has_header=False,
                )
            
            # First row is assumed to be headers
            headers = values[0] if values else []
            data_rows = values[1:] if len(values) > 1 else []
            
            # Build columns
            columns = []
            for col_idx, header in enumerate(headers):
                # Collect sample values for this column
                sample_values = []
                for row in data_rows[:10]:
                    if col_idx < len(row):
                        sample_values.append(row[col_idx])
                
                col = SheetColumn(
                    index=col_idx,
                    header=str(header).strip() if header else f"Column_{col_idx + 1}",
                    letter=self._col_index_to_letter(col_idx),
                    sample_values=sample_values[:5],
                    detected_type=self._detect_column_type(sample_values),
                )
                columns.append(col)
            
            schema = SheetSchema(
                spreadsheet_id=spreadsheet_id,
                spreadsheet_title=spreadsheet_title,
                sheet_name=actual_sheet_name,
                sheet_id=sheet_id,
                columns=columns,
                row_count=len(data_rows),
                has_header=True,
            )
            
            self._schema_cache[cache_key] = schema
            logger.info(f"Detected schema for '{spreadsheet_title}' with {len(columns)} columns")
            return schema
            
        except HttpError as e:
            logger.error(f"Google Sheets API error: {e}")
            raise ValueError(f"Failed to access spreadsheet: {e}")

    def read_all_data(
        self,
        spreadsheet_id: str,
        sheet_name: Optional[str] = None,
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> tuple[SheetSchema, list[SheetData]]:
        """
        Read all data from a sheet with its schema.
        
        Returns:
            Tuple of (schema, list of rows as SheetData)
        """
        schema = self.detect_schema(spreadsheet_id, sheet_name)
        
        if settings.mock_mode:
            return schema, [
                SheetData(row_number=2, data={"Name": "John Doe", "Phone": "+1234567890", "Email": "john@example.com"}),
                SheetData(row_number=3, data={"Name": "Jane Smith", "Phone": "+0987654321", "Email": "jane@example.com"}),
            ]
        
        service = self._get_service()
        if not service:
            return schema, []
        
        try:
            # Calculate range
            start_row = 2 + offset  # Skip header
            end_row = start_row + limit - 1 if limit else 10000
            col_letter = self._col_index_to_letter(len(schema.columns) - 1) if schema.columns else "Z"
            range_name = f"'{schema.sheet_name}'!A{start_row}:{col_letter}{end_row}"
            
            result = service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get("values", [])
            data = []
            
            for row_idx, row in enumerate(values):
                row_data = {}
                for col in schema.columns:
                    if col.index < len(row):
                        row_data[col.header] = row[col.index]
                    else:
                        row_data[col.header] = None
                
                data.append(SheetData(
                    row_number=start_row + row_idx,
                    data=row_data,
                ))
            
            return schema, data
            
        except HttpError as e:
            logger.error(f"Failed to read sheet data: {e}")
            raise ValueError(f"Failed to read data: {e}")

    def get_row(
        self,
        spreadsheet_id: str,
        row_number: int,
        sheet_name: Optional[str] = None,
    ) -> Optional[SheetData]:
        """Get a single row by row number."""
        schema = self.detect_schema(spreadsheet_id, sheet_name)
        
        if settings.mock_mode:
            return SheetData(row_number=row_number, data={"Name": "Mock User", "Phone": "+1234567890"})
        
        service = self._get_service()
        if not service:
            return None
        
        try:
            col_letter = self._col_index_to_letter(len(schema.columns) - 1) if schema.columns else "Z"
            range_name = f"'{schema.sheet_name}'!A{row_number}:{col_letter}{row_number}"
            
            result = service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get("values", [])
            if not values or not values[0]:
                return None
            
            row = values[0]
            row_data = {}
            for col in schema.columns:
                if col.index < len(row):
                    row_data[col.header] = row[col.index]
                else:
                    row_data[col.header] = None
            
            return SheetData(row_number=row_number, data=row_data)
            
        except HttpError as e:
            logger.error(f"Failed to get row: {e}")
            return None

    def update_row(
        self,
        spreadsheet_id: str,
        row_number: int,
        updates: dict[str, Any],
        sheet_name: Optional[str] = None,
    ) -> bool:
        """
        Update specific cells in a row.
        
        Args:
            spreadsheet_id: The Google Sheet ID
            row_number: The row number to update (1-indexed, data starts at 2)
            updates: Dict of column_header -> new_value
            sheet_name: Specific sheet name (optional)
        """
        schema = self.detect_schema(spreadsheet_id, sheet_name)
        
        if settings.mock_mode:
            logger.info(f"MOCK_MODE: Would update row {row_number} with {updates}")
            return True
        
        service = self._get_service()
        if not service:
            return False
        
        try:
            # Build update request
            data = []
            for col in schema.columns:
                if col.header in updates:
                    range_name = f"'{schema.sheet_name}'!{col.letter}{row_number}"
                    data.append({
                        "range": range_name,
                        "values": [[updates[col.header]]]
                    })
            
            if not data:
                logger.warning("No matching columns found for update")
                return False
            
            body = {
                "valueInputOption": "USER_ENTERED",
                "data": data
            }
            
            service.spreadsheets().values().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=body
            ).execute()
            
            logger.info(f"Updated row {row_number} with {len(updates)} values")
            return True
            
        except HttpError as e:
            logger.error(f"Failed to update row: {e}")
            return False

    def append_row(
        self,
        spreadsheet_id: str,
        row_data: dict[str, Any],
        sheet_name: Optional[str] = None,
    ) -> int:
        """
        Append a new row to the sheet.
        
        Args:
            spreadsheet_id: The Google Sheet ID
            row_data: Dict of column_header -> value
            sheet_name: Specific sheet name (optional)
        
        Returns:
            The row number of the new row
        """
        schema = self.detect_schema(spreadsheet_id, sheet_name)
        
        if settings.mock_mode:
            logger.info(f"MOCK_MODE: Would append row: {row_data}")
            return schema.row_count + 2
        
        service = self._get_service()
        if not service:
            return -1
        
        try:
            # Build row values in column order
            values = []
            for col in schema.columns:
                values.append(row_data.get(col.header, ""))
            
            body = {"values": [values]}
            
            result = service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=f"'{schema.sheet_name}'!A:A",
                valueInputOption="USER_ENTERED",
                insertDataOption="INSERT_ROWS",
                body=body
            ).execute()
            
            # Parse the updated range to get row number
            updated_range = result.get("updates", {}).get("updatedRange", "")
            match = re.search(r'(\d+)$', updated_range)
            new_row = int(match.group(1)) if match else schema.row_count + 2
            
            logger.info(f"Appended new row at {new_row}")
            return new_row
            
        except HttpError as e:
            logger.error(f"Failed to append row: {e}")
            return -1

    def delete_row(
        self,
        spreadsheet_id: str,
        row_number: int,
        sheet_name: Optional[str] = None,
    ) -> bool:
        """
        Delete a row from the sheet.
        
        Args:
            spreadsheet_id: The Google Sheet ID
            row_number: The row number to delete (1-indexed)
            sheet_name: Specific sheet name (optional)
        """
        schema = self.detect_schema(spreadsheet_id, sheet_name)
        
        if settings.mock_mode:
            logger.info(f"MOCK_MODE: Would delete row {row_number}")
            return True
        
        service = self._get_service()
        if not service:
            return False
        
        try:
            request = {
                "deleteDimension": {
                    "range": {
                        "sheetId": schema.sheet_id,
                        "dimension": "ROWS",
                        "startIndex": row_number - 1,  # 0-indexed
                        "endIndex": row_number
                    }
                }
            }
            
            service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={"requests": [request]}
            ).execute()
            
            # Invalidate cache
            cache_key = f"{spreadsheet_id}:{sheet_name or 'default'}"
            if cache_key in self._schema_cache:
                del self._schema_cache[cache_key]
            
            logger.info(f"Deleted row {row_number}")
            return True
            
        except HttpError as e:
            logger.error(f"Failed to delete row: {e}")
            return False

    def find_rows(
        self,
        spreadsheet_id: str,
        column_header: str,
        value: str,
        sheet_name: Optional[str] = None,
        exact_match: bool = False,
    ) -> list[SheetData]:
        """
        Find rows where a column matches a value.
        
        Args:
            spreadsheet_id: The Google Sheet ID
            column_header: The column to search
            value: The value to search for
            sheet_name: Specific sheet name (optional)
            exact_match: Whether to require exact match vs contains
        """
        schema, all_data = self.read_all_data(spreadsheet_id, sheet_name)
        
        matches = []
        value_lower = value.lower()
        
        for row in all_data:
            cell_value = row.data.get(column_header, "")
            if cell_value is None:
                continue
            
            cell_str = str(cell_value).lower()
            
            if exact_match:
                if cell_str == value_lower:
                    matches.append(row)
            else:
                if value_lower in cell_str:
                    matches.append(row)
        
        return matches

    def get_column_values(
        self,
        spreadsheet_id: str,
        column_header: str,
        sheet_name: Optional[str] = None,
        unique: bool = False,
    ) -> list[Any]:
        """Get all values from a specific column."""
        schema, all_data = self.read_all_data(spreadsheet_id, sheet_name)
        
        values = []
        for row in all_data:
            val = row.data.get(column_header)
            if val is not None:
                values.append(val)
        
        if unique:
            return list(dict.fromkeys(values))  # Preserve order while removing dupes
        return values

    def add_column(
        self,
        spreadsheet_id: str,
        column_header: str,
        default_value: str = "",
        sheet_name: Optional[str] = None,
    ) -> bool:
        """
        Add a new column to the sheet.
        
        Args:
            spreadsheet_id: The Google Sheet ID
            column_header: Header name for the new column
            default_value: Default value for existing rows
            sheet_name: Specific sheet name (optional)
        """
        schema = self.detect_schema(spreadsheet_id, sheet_name, force_refresh=True)
        
        if settings.mock_mode:
            logger.info(f"MOCK_MODE: Would add column '{column_header}'")
            return True
        
        service = self._get_service()
        if not service:
            return False
        
        try:
            new_col_letter = self._col_index_to_letter(len(schema.columns))
            
            # Add header
            header_range = f"'{schema.sheet_name}'!{new_col_letter}1"
            service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=header_range,
                valueInputOption="USER_ENTERED",
                body={"values": [[column_header]]}
            ).execute()
            
            # Add default values if specified and there are data rows
            if default_value and schema.row_count > 0:
                data_range = f"'{schema.sheet_name}'!{new_col_letter}2:{new_col_letter}{schema.row_count + 1}"
                values = [[default_value]] * schema.row_count
                service.spreadsheets().values().update(
                    spreadsheetId=spreadsheet_id,
                    range=data_range,
                    valueInputOption="USER_ENTERED",
                    body={"values": values}
                ).execute()
            
            # Invalidate schema cache
            cache_key = f"{spreadsheet_id}:{sheet_name or 'default'}"
            if cache_key in self._schema_cache:
                del self._schema_cache[cache_key]
            
            logger.info(f"Added column '{column_header}' at {new_col_letter}")
            return True
            
        except HttpError as e:
            logger.error(f"Failed to add column: {e}")
            return False

    def list_sheets(self, spreadsheet_id: str) -> list[dict]:
        """List all sheets in a spreadsheet."""
        if settings.mock_mode:
            return [{"title": "Sheet1", "sheetId": 0}, {"title": "Sheet2", "sheetId": 1}]
        
        service = self._get_service()
        if not service:
            return []
        
        try:
            result = service.spreadsheets().get(
                spreadsheetId=spreadsheet_id,
                fields="sheets(properties(sheetId,title,gridProperties))"
            ).execute()
            
            sheets = []
            for s in result.get("sheets", []):
                props = s.get("properties", {})
                grid = props.get("gridProperties", {})
                sheets.append({
                    "title": props.get("title", ""),
                    "sheetId": props.get("sheetId", 0),
                    "rowCount": grid.get("rowCount", 0),
                    "columnCount": grid.get("columnCount", 0),
                })
            return sheets
            
        except HttpError as e:
            logger.error(f"Failed to list sheets: {e}")
            return []


# Singleton instance
dynamic_sheets = DynamicSheetsService()
