# ------------------------------------------------------------
# validation.py — Small validation + date helpers
# ------------------------------------------------------------
from typing import Any, Iterable, Mapping
from datetime import datetime, date
from src.conf.errors import InvalidID, InvalidInput, DuplicateID, ImmutableID

def require_int_id(value: Any, field: str = "id") -> int:
    """Make sure an id is an integer > 0."""
    if isinstance(value, bool):
        # bool is a subclass of int; exclude it explicitly
        raise InvalidID(f"{field} must be an integer")
    try:
        iv = int(value)
    except Exception:
        raise InvalidID(f"{field} must be an integer")
    if iv <= 0:
        raise InvalidID(f"{field} must be a positive integer")
    return iv

def ensure_unique_id(rows: Iterable[Mapping], new_id: int, field: str = "id") -> None:
    """Ensure no existing record has the same id."""
    for r in rows:
        if int(r.get(field, -1)) == int(new_id):
            raise DuplicateID(f"id already exists: {new_id}")

def require_fields(payload: Mapping[str, Any], required: list[str]) -> None:
    """Check a set of required fields are present and truthy."""
    missing = [k for k in required if not payload.get(k)]
    if missing:
        raise InvalidInput(("Missing required fields", {"missing": missing}))

def canonicalize(value: Any, allowed: set[str], field: str) -> str:
    """
    Make enum values forgiving: case-insensitive, underscores/spaces ignored.
    Returns the canonical form from 'allowed' or raises InvalidInput.
    """
    if value is None:
        raise InvalidInput((f"Invalid {field}. Allowed: {sorted(allowed)}", {field: value}))
    v = str(value).replace("_", " ").strip().lower()
    for opt in allowed:
        if opt.lower() == v:
            return opt
    raise InvalidInput((f"Invalid {field}. Allowed: {sorted(allowed)}", {field: value}))

def parse_iso_datetime(s: str) -> datetime:
    """
    Parse an ISO datetime string. Accepts 'YYYY-MM-DD' or 'YYYY-MM-DDTHH:MM(:SS)?'
    and common 'Z' suffix. Returns a datetime (naive is fine for this project).
    """
    if not isinstance(s, str) or not s.strip():
        raise InvalidInput(("Invalid date", {"date": s}))
    txt = s.strip()
    # Allow 'Z' suffix as UTC indicator for simple parsing
    if txt.endswith("Z"):
        txt = txt[:-1]
    try:
        if "T" in txt:
            return datetime.fromisoformat(txt)
        # If date only, set time to 00:00:00
        return datetime.fromisoformat(txt + "T00:00:00")
    except Exception:
        raise InvalidInput(("Invalid date", {"date": s}))

def is_today_or_future(dt: datetime) -> bool:
    """Return True if dt is today or later."""
    return dt.date() >= date.today()

def forbid_identity_change(path_id: int, body: Mapping[str, Any], field: str = "id") -> None:
    """Block changes to identity fields during updates."""
    if field in body:
        body_id = require_int_id(body[field], field=field)
        if body_id != path_id:
            raise ImmutableID("ID in body must match path and cannot change")
