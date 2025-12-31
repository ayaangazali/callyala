"""Tests for Google Sheets column mapping."""

import pytest
from app.core.time import normalize_phone_kuwait


class TestPhoneNormalization:
    """Test phone number normalization for Kuwait."""

    def test_normalize_local_format(self):
        """Test normalizing local Kuwait number."""
        # Local format without country code
        result = normalize_phone_kuwait("55123456")
        assert result == "+96555123456"

    def test_normalize_with_country_code(self):
        """Test number already with country code."""
        result = normalize_phone_kuwait("+96555123456")
        assert result == "+96555123456"

    def test_normalize_with_00_prefix(self):
        """Test number with 00 international prefix."""
        result = normalize_phone_kuwait("0096555123456")
        assert result == "+96555123456"

    def test_normalize_strips_spaces(self):
        """Test that spaces are stripped."""
        result = normalize_phone_kuwait("55 12 34 56")
        assert result == "+96555123456"

    def test_normalize_strips_dashes(self):
        """Test that dashes are stripped."""
        result = normalize_phone_kuwait("55-12-34-56")
        assert result == "+96555123456"

    def test_invalid_phone_returns_none(self):
        """Test that invalid phone returns None."""
        result = normalize_phone_kuwait("invalid")
        assert result is None

    def test_empty_phone_returns_none(self):
        """Test that empty string returns None."""
        result = normalize_phone_kuwait("")
        assert result is None


class TestSheetColumnMapping:
    """Test sheet column discovery and mapping."""

    def test_find_column_case_insensitive(self):
        """Test finding columns case-insensitively."""
        headers = ["Name", "PHONE", "Email", "Notes"]
        
        def find_column(headers, *names):
            lower_headers = [h.lower() for h in headers]
            for name in names:
                if name.lower() in lower_headers:
                    return lower_headers.index(name.lower())
            return None
        
        assert find_column(headers, "phone") == 1
        assert find_column(headers, "PHONE") == 1
        assert find_column(headers, "Phone") == 1

    def test_find_column_with_aliases(self):
        """Test finding columns with multiple aliases."""
        headers = ["Full Name", "Mobile", "email_address"]
        
        def find_column(headers, *names):
            lower_headers = [h.lower() for h in headers]
            for name in names:
                if name.lower() in lower_headers:
                    return lower_headers.index(name.lower())
            return None
        
        # Should find "mobile" when looking for phone
        assert find_column(headers, "phone", "mobile", "tel") == 1
        assert find_column(headers, "email", "email_address") == 2

    def test_required_columns_validation(self):
        """Test validation of required columns."""
        required = ["name", "phone"]
        
        # Valid headers
        headers1 = ["Name", "Phone", "Notes"]
        missing1 = [r for r in required if r.lower() not in [h.lower() for h in headers1]]
        assert missing1 == []
        
        # Missing phone
        headers2 = ["Name", "Email"]
        missing2 = [r for r in required if r.lower() not in [h.lower() for h in headers2]]
        assert "phone" in missing2


class TestSheetRowParsing:
    """Test parsing sheet rows into lead data."""

    def test_parse_row_with_all_columns(self):
        """Test parsing row with all expected columns."""
        headers = ["Name", "Phone", "Email", "Car Interest"]
        row = ["John Doe", "55123456", "john@example.com", "Sedan"]
        
        def parse_row(headers, row):
            return {h: row[i] if i < len(row) else "" for i, h in enumerate(headers)}
        
        parsed = parse_row(headers, row)
        assert parsed["Name"] == "John Doe"
        assert parsed["Phone"] == "55123456"
        assert parsed["Email"] == "john@example.com"
        assert parsed["Car Interest"] == "Sedan"

    def test_parse_row_with_missing_values(self):
        """Test parsing row with missing optional values."""
        headers = ["Name", "Phone", "Email", "Notes"]
        row = ["Jane Doe", "55123456"]  # Missing email and notes
        
        def parse_row(headers, row):
            return {h: row[i] if i < len(row) else "" for i, h in enumerate(headers)}
        
        parsed = parse_row(headers, row)
        assert parsed["Name"] == "Jane Doe"
        assert parsed["Phone"] == "55123456"
        assert parsed["Email"] == ""
        assert parsed["Notes"] == ""

    def test_skip_empty_rows(self):
        """Test that empty rows are skipped."""
        rows = [
            ["John", "55123456"],
            ["", ""],  # Empty row
            ["Jane", "55654321"],
        ]
        
        def is_valid_row(row):
            return any(cell.strip() for cell in row if cell)
        
        valid_rows = [r for r in rows if is_valid_row(r)]
        assert len(valid_rows) == 2

    def test_build_lead_object(self):
        """Test building lead object from row."""
        row_data = {
            "name": "Ahmed",
            "phone": "55123456",
            "email": "ahmed@test.com",
            "interest": "SUV"
        }
        
        phone_e164 = normalize_phone_kuwait(row_data["phone"])
        
        lead = {
            "name": row_data["name"],
            "phone_e164": phone_e164,
            "email": row_data.get("email", ""),
            "metadata": {
                "interest": row_data.get("interest", ""),
            }
        }
        
        assert lead["name"] == "Ahmed"
        assert lead["phone_e164"] == "+96555123456"
        assert lead["metadata"]["interest"] == "SUV"
