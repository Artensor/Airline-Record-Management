from __future__ import annotations

from typing import Any, Mapping, Optional

from src.conf.enums import AIRLINE_TYPES
from src.conf.errors import ImmutableID, InvalidInput, NotFound
from src.record.common.search import filter_by_q
from src.record.common.validation import (
    validate_unique_id,
    required_fields,
    validate_int_id
)
from src.record.airlines.repo import AirlinesRepo, get_repo

# simple normalize helpers
def _norm(x: Any) -> str:
    return str(x or "").strip()

def _eq_ci(a: Any, b: Any) -> bool:
    return _norm(a).lower() == _norm(b).lower()

# fields we search over (case-insensitive)
_SEARCH_FIELDS = ["id", "company_name", "type"]

# allowed sort keys
_ALLOWED_SORTS = {"id", "company_name", "type"}

DEFAULT_LIMIT = 50
MAX_LIMIT = 200

def _safe_sort_key(key: str):
    k = key if key in _ALLOWED_SORTS else "id"
    def _key(rec: Mapping[str, Any]):
        v = rec.get(k)
        if k == "id":
            try:
                return int(v) if v is not None else 0
            except Exception:
                return 0
        return str(v or "").lower()
    return _key

def _validate_required(payload: Mapping[str, Any]) -> None:
    required_fields(payload, ["id", "type", "company_name"])

def _validate_formats(payload: Mapping[str, Any]) -> None:
    # No-op: we canonicalize `type` with _canonical_airline_type().
    return

def _canonical_airline_type(value: Any) -> str:
    """
    Accepts 'national', 'National', 'low_cost', etc., and returns
    the canonical value from AIRLINE_TYPES (e.g., 'National', 'Low Cost').
    """
    v = _norm(value).replace("_", " ").lower()
    for opt in AIRLINE_TYPES:
        if opt.lower() == v:
            return opt
    raise InvalidInput(f"Invalid type. Allowed: {sorted(AIRLINE_TYPES)}", {"type": value})

def create_airline(payload: Mapping[str, Any], repo: Optional[AirlinesRepo] = None) -> dict:
    repo = repo or get_repo()
    _validate_required(payload)
    airline_id = validate_int_id(payload.get("id"), field="id")
    validate_unique_id(repo.list_all(), airline_id, field="id")

    record = dict(payload)
    record["type"] = _canonical_airline_type(record.get("type"))
    return repo.insert(record)

def update_airline(airline_id: int, updates: Mapping[str, Any], repo: Optional[AirlinesRepo] = None) -> dict:
    repo = repo or get_repo()
    airline_id = validate_int_id(airline_id, field="id")
    if "id" in updates:
        body_id = validate_int_id(updates["id"], field="id")
        if body_id != airline_id:
            raise ImmutableID("ID in body must match path and cannot change")
    existing = repo.get_by_id(airline_id)
    if not existing:
        raise NotFound(f"Airline {airline_id} not found")
    
    patch = dict(updates)
    if "type" in patch:
        patch["type"] = _canonical_airline_type(patch["type"])
    return repo.update(airline_id, patch)

def delete_airline(airline_id: int, repo: Optional[AirlinesRepo] = None) -> None:
    repo = repo or get_repo()
    airline_id = validate_int_id(airline_id, field="id")
    if not repo.delete(airline_id):
        raise NotFound(f"Airline {airline_id} not found")

def get_airline(airline_id: int, repo: Optional[AirlinesRepo] = None) -> dict:
    repo = repo or get_repo()
    airline_id = validate_int_id(airline_id, field="id")
    rec = repo.get_by_id(airline_id)
    if not rec:
        raise NotFound(f"Airline {airline_id} not found")
    return rec

def list_airlines(repo: Optional[AirlinesRepo] = None, *, limit: int = DEFAULT_LIMIT, offset: int = 0, sort: str = "id") -> dict:
    """
    List with pagination (kept like Clients for now).
    """
    repo = repo or get_repo()
    try:
        limit = max(0, min(int(limit), MAX_LIMIT))
        offset = max(0, int(offset))
    except Exception:
        raise InvalidInput("limit/offset must be integers")
    sort_key = (_norm(sort).lower() or "id")
    if sort_key not in _ALLOWED_SORTS:
        raise InvalidInput(f"Invalid sort key. Allowed: {sorted(_ALLOWED_SORTS)}")
    items = repo.list_all()
    items_sorted = sorted(items, key=_safe_sort_key(sort_key))
    return {
        "data": items_sorted[offset: offset + limit] if limit > 0 else items_sorted[offset:],
        "count": len(items_sorted),
        "limit": limit,
        "offset": offset,
        "sort": sort_key,
    }

def search_airlines(repo: Optional[AirlinesRepo] = None, *, q: str = "", type: str | None = None, sort: str = "id") -> dict:
    """
    Search returns ALL matches (no pagination). This is the one change from Clients.
    """
    repo = repo or get_repo()
    sort_key = (_norm(sort).lower() or "id")
    if sort_key not in _ALLOWED_SORTS:
        raise InvalidInput(f"Invalid sort key. Allowed: {sorted(_ALLOWED_SORTS)}")
    items = repo.list_all()
    items = filter_by_q(items, _SEARCH_FIELDS, q)
    if _norm(type):
        items = [r for r in items if _eq_ci(r.get("type"), type)]
    items_sorted = sorted(items, key=_safe_sort_key(sort_key))
    return {
        "data": items_sorted,
        "count": len(items_sorted),
        "sort": sort_key,
    }
