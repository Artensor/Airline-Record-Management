# ------------------------------------------------------------
# service.py (airlines) — Validation + business rules for airlines
# ------------------------------------------------------------
from typing import Any, Mapping, Optional
from src.conf.enums import AIRLINE_TYPES
from src.conf.errors import InvalidInput
from src.record.common.validation import (
    require_int_id, ensure_unique_id, require_fields, canonicalize, forbid_identity_change
)
from src.record.airlines.repo import AirlinesRepo, get_repo
from src.record.flights.repo import get_repo as get_flights_repo
from src.record.common.validation import parse_iso_datetime, is_today_or_future

REQUIRED_FIELDS = ["id", "type", "company_name"]
# Check if the airline has flights today or in the future and avoid deletion if so.
def _has_future_flights_for_airline(airline_id: int) -> bool:
    """Check if the airline has flights today or in the future."""
    frepo = get_flights_repo()
    for f in frepo.list_all():
        if int(f.get("airline_id", -1)) == int(airline_id):
            try:
                dt = parse_iso_datetime(f.get("date", ""))
                if is_today_or_future(dt):
                    return True
            except Exception:
                continue
    return False
# Create a new airline record after validating required fields and uniqueness.
def create_airline(payload: Mapping[str, Any], repo: Optional[AirlinesRepo] = None) -> dict:
    """Create an airline after basic validation."""
    repo = repo or get_repo()
    require_fields(payload, REQUIRED_FIELDS)
    airline_id = require_int_id(payload.get("id"), field="id")
    ensure_unique_id(repo.list_all(), airline_id, field="id")
    record = dict(payload)
    record["type"] = canonicalize(record.get("type"), AIRLINE_TYPES, field="type")
    return repo.insert(record)
# Retrieve a specific airline by its ID, raising NotFound if it doesn't exist.
def get_airline(airline_id: int, repo: Optional[AirlinesRepo] = None) -> dict:
    """Return one airline by id or raise NotFound."""
    repo = repo or get_repo()
    airline_id = require_int_id(airline_id, field="id")
    return repo.get_by_id(airline_id)
# Update an existing airline record with allowed fields only.
def update_airline(airline_id: int, updates: Mapping[str, Any], repo: Optional[AirlinesRepo] = None) -> dict:
    """Update allowed fields; id cannot change."""
    repo = repo or get_repo()
    airline_id = require_int_id(airline_id, field="id")
    forbid_identity_change(airline_id, updates, field="id")
    patch = dict(updates)
    if "type" in patch:
        patch["type"] = canonicalize(patch["type"], AIRLINE_TYPES, field="type")
    return repo.update(airline_id, patch)
# Delete an airline if there are no flights today or in the future associated with it.
def delete_airline(airline_id: int, repo: Optional[AirlinesRepo] = None) -> None:
    """Delete if there are no today/future flights for this airline."""
    repo = repo or get_repo()
    airline_id = require_int_id(airline_id, field="id")
    if _has_future_flights_for_airline(airline_id):
        raise InvalidInput("Cannot delete airline: future or today flights exist")
    if not repo.delete(airline_id):
        from src.conf.errors import NotFound
        raise NotFound(f"Airline {airline_id} not found")
# Search airlines by company name with optional sorting.
def search_airlines(q: str = "", sort: str = "company_name", repo: Optional[AirlinesRepo] = None) -> dict:
    """
    Simple search (no pagination):
      - q matches company_name (case-insensitive)
      - sort by given field, defaults to company_name
    Returns: {"count": N, "data": [ ... ]}
    """
    repo = repo or get_repo()
    q = (q or "").strip().lower()
    rows = repo.list_all()
    if q:
        rows = [r for r in rows if q in str(r.get("company_name", "")).lower()]
    try:
        rows.sort(key=lambda r: r.get(sort, rows))
    except Exception:
        rows.sort(key=lambda r: r.get("company_name", rows))
    return {"count": len(rows), "data": rows}