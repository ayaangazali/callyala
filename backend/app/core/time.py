"""Timezone and time utilities."""

from datetime import datetime, timezone
from typing import Optional

import pytz

from .config import settings


def now_utc() -> datetime:
    """Get current UTC datetime."""
    return datetime.now(timezone.utc)


def now_local(tz: Optional[str] = None) -> datetime:
    """Get current datetime in local timezone."""
    tz_name = tz or settings.default_timezone
    local_tz = pytz.timezone(tz_name)
    return datetime.now(local_tz)


def to_local(dt: datetime, tz: Optional[str] = None) -> datetime:
    """Convert UTC datetime to local timezone."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    tz_name = tz or settings.default_timezone
    local_tz = pytz.timezone(tz_name)
    return dt.astimezone(local_tz)


def to_utc(dt: datetime) -> datetime:
    """Convert datetime to UTC."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def parse_datetime(value: str) -> datetime:
    """Parse ISO datetime string."""
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return to_utc(dt)


def format_datetime(dt: datetime, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format datetime for display."""
    return dt.strftime(fmt)


def format_iso(dt: datetime) -> str:
    """Format datetime as ISO string."""
    return dt.isoformat()


def normalize_phone_kuwait(phone: str) -> Optional[str]:
    """
    Normalize a phone number to E.164 format for Kuwait (+965).
    
    Handles various input formats:
    - Local: 55123456 -> +96555123456
    - With country code: +96555123456 -> +96555123456
    - With 00 prefix: 0096555123456 -> +96555123456
    - With spaces/dashes: 55 12 34 56 -> +96555123456
    
    Returns None if phone is invalid.
    """
    if not phone:
        return None
    
    # Remove spaces, dashes, parentheses
    cleaned = phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    
    # Handle various prefixes
    if cleaned.startswith("+965"):
        # Already has country code
        number = cleaned
    elif cleaned.startswith("00965"):
        # International format with 00
        number = "+" + cleaned[2:]
    elif cleaned.startswith("965"):
        # Country code without +
        number = "+" + cleaned
    elif len(cleaned) == 8 and cleaned.isdigit():
        # Local 8-digit Kuwait number
        number = "+965" + cleaned
    else:
        # Try to parse anyway
        try:
            import phonenumbers
            parsed = phonenumbers.parse(cleaned, "KW")
            if phonenumbers.is_valid_number(parsed):
                return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        except Exception:
            pass
        return None
    
    # Validate the resulting number
    try:
        import phonenumbers
        parsed = phonenumbers.parse(number, "KW")
        if phonenumbers.is_valid_number(parsed):
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    except Exception:
        pass
    
    # If phonenumbers validation fails but format looks right, return it
    if number.startswith("+965") and len(number) == 12:
        return number
    
    return None
