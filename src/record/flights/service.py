# ------------------------------------------------------------
# service.py (flights) — Validation + rules for flights
# ------------------------------------------------------------
from typing import Any, Mapping, Optional
from datetime import datetime
from src.conf.errors import InvalidInput, ImmutableID, NotFound
from src.record.common.validation import (
    require_int_id, require_fields, parse_iso_datetime, is_today_or_future
)
from src.record.flights.repo import FlightsRepo, get_repo
from src.record.clients.repo import get_repo as get_clients_repo
from src.record.airlines.repo import get_repo as get_airlines_repo

REQUIRED_FIELDS = ["client_id", "airline_id", "date", "start_city", "end_city"]
# Helper to check foreign keys exist
def _exists_client(client_id: int) -> bool:
    try:
        get_clients_repo().get_by_id(client_id)
        return True
    except Exception:
        return False
# Helper to check foreign keys exist
def _exists_airline(airline_id: int) -> bool:
    try:
        get_airlines_repo().get_by_id(airline_id)
        return True
    except Exception:
        return False
# Create a new flight
def create_flight(payload: Mapping[str, Any], repo: Optional[FlightsRepo] = None) -> dict:
    """
    Create a flight. Identity is (client_id, airline_id, date).
    Rejects duplicates and validates foreign keys exist (client/airline).
    """
    repo = repo or get_repo()
    require_fields(payload, REQUIRED_FIELDS)
    client_id = require_int_id(payload.get("client_id"), field="client_id")
    airline_id = require_int_id(payload.get("airline_id"), field="airline_id")
    date_txt = str(payload.get("date"))
    flight_dt = parse_iso_datetime(date_txt)

    if not _exists_client(client_id):
        raise InvalidInput(("Unknown client_id", {"client_id": client_id}))
    if not _exists_airline(airline_id):
        raise InvalidInput(("Unknown airline_id", {"airline_id": airline_id}))

    # enforce uniqueness
    for f in repo.list_all():
        if int(f.get("client_id", -1)) == client_id and int(f.get("airline_id", -1)) == airline_id and f.get("date") == date_txt:
            raise InvalidInput("Flight already exists for this client/airline/date")

    record = {
        "client_id": client_id,
        "airline_id": airline_id,
        "date": date_txt,
        "start_city": payload.get("start_city"),
        "end_city": payload.get("end_city"),
    }
    return repo.insert(record)
# Get a flight by its composite identity
def get_flight(client_id: int, airline_id: int, date: str, repo: Optional[FlightsRepo] = None) -> dict:
    repo = repo or get_repo()
    client_id = require_int_id(client_id, field="client_id")
    airline_id = require_int_id(airline_id, field="airline_id")
    parse_iso_datetime(date)  # validate format; identity uses the raw string
    return repo.get_one(client_id, airline_id, date)
# Update a flight
def update_flight(client_id: int, airline_id: int, date: str, updates: Mapping[str, Any], repo: Optional[FlightsRepo] = None) -> dict:
    """
    Update a flight. Identity fields (client_id, airline_id, date) cannot change.
    """
    repo = repo or get_repo()
    client_id = require_int_id(client_id, field="client_id")
    airline_id = require_int_id(airline_id, field="airline_id")
    parse_iso_datetime(date)

    # block identity change
    for k in ("client_id", "airline_id", "date"):
        if k in updates and str(updates[k]) != (str(client_id) if k != "date" else date):
            raise ImmutableID(f"{k} cannot change")

    patch = dict(updates)
    if "date" in patch:
        parse_iso_datetime(str(patch["date"]))
    return repo.update(client_id, airline_id, date, patch)
# Delete a flight by its composite identity
def delete_flight(client_id: int, airline_id: int, date: str, repo: Optional[FlightsRepo] = None) -> None:
    """Delete a flight by its composite identity."""
    repo = repo or get_repo()
    client_id = require_int_id(client_id, field="client_id")
    airline_id = require_int_id(airline_id, field="airline_id")
    parse_iso_datetime(date)
    ok = repo.delete(client_id, airline_id, date)
    if not ok:
        raise NotFound("Flight not found")
# List flights with filtering and sorting
def list_flights(q: str = "", client_id: Optional[int] = None, airline_id: Optional[int] = None, repo: Optional[FlightsRepo] = None) -> dict:
    """
    List flights for today and the future only, ordered by date ascending.
    Optional filters:
      - q (matches start_city or end_city, case-insensitive)
      - client_id / airline_id
    Returns: {"count": N, "data": [ ... ]}
    """
    repo = repo or get_repo()
    ql = (q or "").strip().lower()
    rows = []
    for f in repo.list_all():
        try:
            dt = parse_iso_datetime(f.get("date", ""))
        except Exception:
            continue  # skip malformed
        if not is_today_or_future(dt):
            continue
        if client_id and int(f.get("client_id", -1)) != int(client_id):
            continue
        if airline_id and int(f.get("airline_id", -1)) != int(airline_id):
            continue
        if ql and ql not in str(f.get("start_city", "")).lower() and ql not in str(f.get("end_city", "")).lower():
            continue
        rows.append(f)
    rows.sort(key=lambda r: parse_iso_datetime(r["date"]))
    return {"count": len(rows), "data": rows}
