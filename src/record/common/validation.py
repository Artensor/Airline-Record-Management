"""Code to validate formats and other input rules.
These helpers are pure functions used by service layers to enforce input
rules.
"""
from __future__ import annotations
import re
from typing import Iterable, Mapping, Any
from dateutil import parser
from zoneinfo import ZoneInfo

from src.conf.errors import InvalidID, InvalidInput, DuplicateID
from src.conf.enums import CLIENT_TYPES, AIRLINE_TYPES

# Liberal, human-friendly formats; not country-specific but pragmatic.
PHONE_RE = re.compile(r"^[+\d][\d\s().-]{6,}$")
ZIP_RE = re.compile(r"^[\w\s-]{3,12}$")

def validate_int_id(value: Any, field: str = "id") -> int:
    """Validate and coerce an ID field into a positive integer.
    Args:
        value: The provided ID value (string/int).
        field: Field name for error messages.
    Returns:
        The integer ID (guaranteed > 0).
    Raises:
        InvalidID: If parsing fails or value <= 0.
    """
    try:
        iv = int(value)
    except (ValueError, TypeError):
        raise InvalidID(f"{field} must be an integer")
    if iv <= 0:
        raise InvalidID(f"{field} must be > 0")
    return iv

def validate_unique_id(items: Iterable[Mapping[str, Any]], candidate_id: int, field: str = "id") -> None:
    """Ensure candidate_id is not already present among items.

    Args:
        items: Iterable of dict-like records with 'id' fields.
        candidate_id: The ID to validate.
        field: Name of the ID field (usually 'id').

    Raises:
        DuplicateID: If an existing record has the same ID.
    """
    if any(int(x.get(field, -1)) == candidate_id for x in items):
        raise DuplicateID(f"{field} already exists: {candidate_id}")


def required_fields(payload: Mapping[str, Any], fields: Iterable[str]) -> None:
    """Assert that required fields are present and non-empty strings.
    Args:
        payload: Input mapping (e.g., request JSON).
        fields: Iterable of required field names.
    Raises:
        InvalidInput: If any required field is missing/empty.
    """
    missing = [f for f in fields if not str(payload.get(f, "")).strip()]
    if missing:
        raise InvalidInput("Missing required fields", {"missing": missing})

def validate_enum(value: str, allowed: set[str], field: str = "type") -> None:
    """Validate that a value belongs to an allowed set.
    Args:
        value: Provided string value.
        allowed: Allowed string values for the field.
        field: Field name for error messages.
    Raises:
        InvalidInput: If the value is not in the allowed set.
    """
    if value not in allowed:
        raise InvalidInput(f"Invalid {field}. Allowed: {sorted(allowed)}", {field: value})

def validate_phone(phone: str) -> None:
    """Validate phone number format.
    Args:
        phone: Phone number string.
    Raises:
        InvalidInput: If the format doesn't match the regex.
    """
    if not PHONE_RE.match(phone):
        raise InvalidInput("Invalid phone number format", {"phone_number": phone})

def validate_zip(zip_code: str) -> None:
    """Validate zip/postal code format.
    Args:
        zip_code: Zip/postal code string.
    Raises:
        InvalidInput: If the format doesn't match the regex.
    """
    if not ZIP_RE.match(zip_code):
        raise InvalidInput("Invalid zip/postal code format", {"zip_code": zip_code})

def parse_datetime_to_utc(dt_str: str, default_tz: str) -> str:
    """Parse an ISO-like datetime string and return a UTC ISO string.
    Args:
        dt_str: ISO-like datetime string (e.g., "2025-10-03T14:30:00-06:00").
        default_tz: Time zone name for naive inputs (e.g., "America/Costa_Rica").
    Returns:
        ISO-8601 string in UTC.
    Raises:
        InvalidInput: If dt_str is blank or can't be parsed.
    """
    if not dt_str or not str(dt_str).strip():
        raise InvalidInput("Date/time is required")
    dt = parser.isoparse(str(dt_str).strip())
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo(default_tz))
    dt_utc = dt.astimezone(ZoneInfo("UTC"))
    return dt_utc.isoformat()