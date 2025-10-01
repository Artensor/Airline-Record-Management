# ------------------------------------------------------------
# service.py (clients) — Validation + business rules for clients
# ------------------------------------------------------------
from typing import Any, Mapping, Optional
from src.conf.enums import CLIENT_TYPES
from src.conf.errors import InvalidInput
from src.record.common.validation import (
    require_int_id, ensure_unique_id, require_fields, canonicalize, forbid_identity_change
)
from src.record.clients.repo import ClientsRepo, get_repo
from src.record.flights.repo import get_repo as get_flights_repo
from src.record.common.validation import parse_iso_datetime, is_today_or_future

REQUIRED_FIELDS = [
    "id", "type", "name", "address_line1", "city", "state", "zip_code", "country", "phone_number"
]
#Check if client has future flights
def _has_future_flights_for_client(client_id: int) -> bool:
    """Check if the client has flights today or in the future."""
    frepo = get_flights_repo()
    for f in frepo.list_all():
        if int(f.get("client_id", -1)) == int(client_id):
            try:
                dt = parse_iso_datetime(f.get("date", ""))
                if is_today_or_future(dt):
                    return True
            except Exception:
                # If date is broken, ignore it here (service won't create broken ones).
                continue
    return False
# Create a new client
def create_client(payload: Mapping[str, Any], repo: Optional[ClientsRepo] = None) -> dict:
    """Create a client after basic validation."""
    repo = repo or get_repo()
    require_fields(payload, REQUIRED_FIELDS)
    client_id = require_int_id(payload.get("id"), field="id")
    ensure_unique_id(repo.list_all(), client_id, field="id")
    record = dict(payload)
    record["type"] = canonicalize(record.get("type"), CLIENT_TYPES, field="type")
    return repo.insert(record)
# Get a client by ID
def get_client(client_id: int, repo: Optional[ClientsRepo] = None) -> dict:
    """Return one client by id or raise NotFound."""
    repo = repo or get_repo()
    client_id = require_int_id(client_id, field="id")
    return repo.get_by_id(client_id)
# Update an existing client
def update_client(client_id: int, updates: Mapping[str, Any], repo: Optional[ClientsRepo] = None) -> dict:
    """Update allowed fields; id cannot change."""
    repo = repo or get_repo()
    client_id = require_int_id(client_id, field="id")
    forbid_identity_change(client_id, updates, field="id")
    patch = dict(updates)
    if "type" in patch:
        patch["type"] = canonicalize(patch["type"], CLIENT_TYPES, field="type")
    return repo.update(client_id, patch)
# Delete a client by ID
def delete_client(client_id: int, repo: Optional[ClientsRepo] = None) -> None:
    """Delete if there are no today/future flights for this client."""
    repo = repo or get_repo()
    client_id = require_int_id(client_id, field="id")
    if _has_future_flights_for_client(client_id):
        raise InvalidInput("Cannot delete client: future or today flights exist")
    if not repo.delete(client_id):
        # Make it consistent: deleting a missing resource is an error
        from src.conf.errors import NotFound
        raise NotFound(f"Client {client_id} not found")
# Search clients with simple filtering and sorting
def search_clients(q: str = "", sort: str = "id", repo: Optional[ClientsRepo] = None) -> dict:
    """
    Simple search (no pagination):
      - q matches name or city (case-insensitive)
      - sort by 'id' or any present field; defaults to 'id' if unknown
    Returns: {"count": N, "data": [ ... ]}
    """
    repo = repo or get_repo()
    q = (q or "").strip().lower()
    rows = repo.list_all()
    if q:
        rows = [r for r in rows if q in str(r.get("name", "")).lower() or q in str(r.get("city", "")).lower()]
    try:
        rows.sort(key=lambda r: r.get(sort, rows))
    except Exception:
        rows.sort(key=lambda r: r.get("id", rows))
    return {"count": len(rows), "data": rows}
