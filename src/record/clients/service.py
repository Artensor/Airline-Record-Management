"""Clients service: business logic, validation, and search for Client records.
This module implements the domain rules for Client entities and exposes
functions that the API layer calls.
"""

from typing import Any, Iterable, Mapping, Optional, Sequence
from src.conf.enums import CLIENT_TYPES
from src.conf.errors import ImmutableID, InvalidInput, NotFound
from src.record.common.search import filter_by_q
from src.record.common.validation import (
    validate_unique_id,
    required_fields,
    validate_int_id,
    validate_enum,
    validate_phone,
    validate_zip,
)
from src.record.clients.repo import ClientsRepo, get_repo

# --------- Configuration for search / pagination ---------
# Which fields are searched when 'q' is provided.
_SEARCH_FIELDS = ["id", "name", "city", "country", "phone_number"]
# Allowed sort keys
_ALLOWED_SORTS = {"id", "name", "city", "state", "country", "type"}

DEFAULT_LIMIT = 50
MAX_LIMIT = 200

# --------- Helpers ---------
def _coerce_bool(value: Any, default: bool = False) -> bool:
    """Coerce common truthy/falsy strings to bool."""
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "on"}

def _normalize_text(s: Any) -> str:
    """Return a trimmed string ('' for None)."""
    return str(s or "").strip()

def _equals_ci(a: Any, b: Any) -> bool:
    """Case-insensitive equality for strings; numeric-safe."""
    return str(a or "").strip().lower() == str(b or "").strip().lower()

def _apply_exact_filters(items: Iterable[Mapping[str, Any]], **filters: Any) -> Sequence[dict]:
    """Filter by exact matches for provided fields."""
    filtered = list(items)
    for field, val in filters.items():
        if _normalize_text(val):
            filtered = [r for r in filtered if _equals_ci(r.get(field), val)]
    return [dict(r) for r in filtered]

def _safe_sort_key(key: str):
    """Return a sort key function for allowed fields; fallback to 'id'."""
    k = key if key in _ALLOWED_SORTS else "id"
    def _key(rec: Mapping[str, Any]):
        # Ensure we don't crash if the field is missing.
        val = rec.get(k)
        # Keep numeric ordering for id if possible, otherwise string order.
        if k == "id":
            try:
                return int(val if val is not None else 0)
            except Exception:
                return 0
        return str(val or "").lower()
    return _key

def _validate_required_client_fields(payload: Mapping[str, Any]) -> None:
    required_fields(
        payload,
        [
            "id",            # user-supplied
            "type",          # enum
            "name"
        ],
    )

def _validate_client_formats(payload: Mapping[str, Any]) -> None:
    """Validate enum/format-specific client fields."""
    validate_enum(_normalize_text(payload.get("type")), CLIENT_TYPES, field="type")
    validate_phone(_normalize_text(payload.get("phone_number")))
    validate_zip(_normalize_text(payload.get("zip_code")))

# --------- Service API ---------
def create_client(
    payload: Mapping[str, Any],
    repo: Optional[ClientsRepo] = None,
) -> dict:
    """Create a new client after validating input rules.
    Args:
        payload: Request body dict containing all client fields.
                 Must include an integer 'id'.
    Returns:
        The created client dict.
    """
    repo = repo or get_repo()

    # 1) Required fields present?
    _validate_required_client_fields(payload)

    # 2) Validate ID and ensure uniqueness against current storage.
    client_id = validate_int_id(payload.get("id"), field="id")
    validate_unique_id(repo.list_all(), client_id, field="id")

    # 3) Validate enums & formats (type/phone/zip).
    _validate_client_formats(payload)

    # 4) Optional address lines: convert empty strings to None for consistency.
    record = dict(payload)
    for opt in ("address_line2", "address_line3"):
        if not _normalize_text(record.get(opt)):
            record[opt] = None

    # 5) Insert and (auto)save via repo. Service returns the stored record.
    return repo.insert(record)

def update_client(
    client_id: int,
    updates: Mapping[str, Any],
    repo: Optional[ClientsRepo] = None,
) -> dict:
    """Update an existing client (ID is immutable).
    Args:
        client_id: The target client's ID (from path param).
        updates:   Partial or full record fields to update (id cannot change).
        repo:      Optional repo instance.
    Returns:
        The updated client dict.
    """
    repo = repo or get_repo()

    # 1) Validate path ID.
    client_id = validate_int_id(client_id, field="id")

    # 2) ID is immutable: if 'id' provided in body, it must match path.
    if "id" in updates:
        body_id = validate_int_id(updates["id"], field="id")
        if body_id != client_id:
            raise ImmutableID("ID in body must match path and cannot change")

    # 3) Ensure target exists before attempting update.
    existing = repo.get_by_id(client_id)
    if not existing:
        raise NotFound(f"Client {client_id} not found")

    # 4) Validate updated fields.
    if "type" in updates:
        validate_enum(_normalize_text(updates["type"]), CLIENT_TYPES, field="type")
    if "phone_number" in updates:
        validate_phone(_normalize_text(updates["phone_number"]))
    if "zip_code" in updates:
        validate_zip(_normalize_text(updates["zip_code"]))

    # 5) Normalize optional address fields.
    patch = dict(updates)
    for opt in ("address_line2", "address_line3"):
        if opt in patch and not _normalize_text(patch.get(opt)):
            patch[opt] = None

    # 6) Apply update in repo; repo enforces "id" not overwritten.
    return repo.update(client_id, patch)

def delete_client(client_id: int, repo: Optional[ClientsRepo] = None) -> None:
    """Delete a client by ID.
    Args:
        client_id: The unique ID of the client to delete.
        repo:      Optional repo instance.
    """
    repo = repo or get_repo()
    client_id = validate_int_id(client_id, field="id")
    ok = repo.delete(client_id)
    if not ok:
        raise NotFound(f"Client {client_id} not found")

def get_client(client_id: int, repo: Optional[ClientsRepo] = None) -> dict:
    """Get a single client by ID or raise NotFound.
    Args:
        client_id: The unique client ID.
        repo:      Optional repo instance.
    Returns:
        The client dict.
    """
    repo = repo or get_repo()
    client_id = validate_int_id(client_id, field="id")
    rec = repo.get_by_id(client_id)
    if not rec:
        raise NotFound(f"Client {client_id} not found")
    return rec

def list_clients(
    repo: Optional[ClientsRepo] = None,
    *,
    limit: int = DEFAULT_LIMIT,
    offset: int = 0,
    sort: str = "id",
) -> dict:
    """Return clients
    Args:
        repo:   Optional repo instance.
        limit:  Page size
        offset: Start index (default 0).
        sort:   Sort key (one of: id, name, city, state, country, type).
    Returns:
        Envelope dict: {"data": [...], "count": N, "limit": x, "offset": y, "sort": key}
    """
    repo = repo or get_repo()

    # Validate paging & sort
    try:
        limit = max(0, min(int(limit), MAX_LIMIT))
        offset = max(0, int(offset))
    except Exception:
        raise InvalidInput("limit/offset must be integers")

    sort_key = _normalize_text(sort).lower() or "id"
    if sort_key not in _ALLOWED_SORTS:
        raise InvalidInput(f"Invalid sort key. Allowed: {sorted(_ALLOWED_SORTS)}")

    items = repo.list_all()
    items_sorted = sorted(items, key=_safe_sort_key(sort_key))
    count = len(items_sorted)
    window = items_sorted[offset : offset + limit] if limit > 0 else items_sorted[offset:]
    return {
        "data": window,
        "count": count,
        "limit": limit,
        "offset": offset,
        "sort": sort_key,
    }

def search_clients(
    repo: Optional[ClientsRepo] = None,
    *,
    q: str = "",
    type: str | None = None,
    city: str | None = None,
    state: str | None = None,
    country: str | None = None,
    limit: int = DEFAULT_LIMIT,
    offset: int = 0,
    sort: str = "id",
) -> dict:
    """Search clients by free text + exact filters, with deterministic paging.
    Filtering rules:
        - 'q' is a case-insensitive substring match across: id, name, city,
          country, phone_number.
        - 'type', 'city', 'state', 'country' are exact, case-insensitive matches.
    Args:
        repo:    Optional repo instance.
        q:       Free-text query.
        type:    Client type (enum).
        city:    Exact city filter (case-insensitive).
        state:   Exact state filter.
        country: Exact country filter.
        limit:   Page size (default 50; capped at MAX_LIMIT).
        offset:  Start index (default 0).
        sort:    Sort key (id|name|city|state|country|type).
    Returns:
        Envelope dict: {"data": [...], "count": N, "limit": x, "offset": y, "sort": key}
    """
    repo = repo or get_repo()

    # Validate paging & sort early.
    try:
        limit = max(0, min(int(limit), MAX_LIMIT))
        offset = max(0, int(offset))
    except Exception:
        raise InvalidInput("limit/offset must be integers")

    sort_key = _normalize_text(sort).lower() or "id"
    if sort_key not in _ALLOWED_SORTS:
        raise InvalidInput(f"Invalid sort key. Allowed: {sorted(_ALLOWED_SORTS)}")

    # Start with all items.
    items = repo.list_all()

    # Free-text filter across selected fields.
    items = filter_by_q(items, _SEARCH_FIELDS, q)

    # Exact filters (case-insensitive) for type/city/state/country.
    items = _apply_exact_filters(items, type=type, city=city, state=state, country=country)

    # Deterministic sort then paginate.
    items_sorted = sorted(items, key=_safe_sort_key(sort_key))
    count = len(items_sorted)
    window = items_sorted[offset : offset + limit] if limit > 0 else items_sorted[offset:]

    return {
        "data": window,
        "count": count,
        "limit": limit,
        "offset": offset,
        "sort": sort_key,
    }