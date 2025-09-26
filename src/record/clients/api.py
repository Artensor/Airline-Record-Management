"""Clients API to serve the UI.
Routes:
    GET    /api/v1/clients
    GET    /api/v1/clients/<id>
    POST   /api/v1/clients
    PUT    /api/v1/clients/<id>
    DELETE /api/v1/clients/<id>

Design:
    - The API layer is intentionally thin: it parses HTTP input and calls
      the service layer, which owns validation and business rules.
    - DomainError exceptions are converted to JSON errors by the global
      error handler registered in src/main.py.
"""

from __future__ import annotations
from flask import Blueprint, jsonify, request, url_for
from src.conf.errors import InvalidInput

from src.record.clients.service import (
    create_client,
    get_client,
    update_client,
    delete_client,
    list_clients,
    search_clients,
    DEFAULT_LIMIT,
)

# NOTE: We do NOT set the url_prefix here, so tests and main.py can register
#       this connections under a base like /api/v1/clients.
bp = Blueprint("clients", __name__)

@bp.get("/")
def list_or_search():
    """List or search clients with
    Query parameters:
        q (str, optional): Free-text search across id, name, city, country, phone_number.
        type (str, optional): Exact match (case-insensitive) for client type (enum).
        city (str, optional): Exact match (case-insensitive).
        state (str, optional): Exact match (case-insensitive).
        country (str, optional): Exact match (case-insensitive).
        limit (int, optional): Page size. Default: 50. Max: 200.
        offset (int, optional): Start index. Default: 0.
        sort (str, optional): One of: id, name, city, state, country, type. Default: id.

    Responses:
        200 OK: JSON:
            {
              "data": [ {client}, ... ],
              "count": <int>,   # total after filtering
              "limit": <int>,
              "offset": <int>,
              "sort": "<key>"
            }
        422 Invalid execution

    Notes:
        - If any filter (q/type/city/state/country) is provided, this endpoint
          performs a search; otherwise it returns a plain list with sorting/paging.
        - IDs are integers in responses.
    """
    args = request.args

    # Pull paging/sort with safe defaults; service revalidates them.
    limit = args.get("limit", default=DEFAULT_LIMIT, type=int)
    offset = args.get("offset", default=0, type=int)
    sort = args.get("sort", default="id", type=str)

    # If any filter is present, use search; else list.
    q = args.get("q")
    f_type = args.get("type")
    city = args.get("city")
    state = args.get("state")
    country = args.get("country")

    if any([q, f_type, city, state, country]):
        result = search_clients(
            q=q or "",
            type=f_type,
            city=city,
            state=state,
            country=country,
            limit=limit,
            offset=offset,
            sort=sort,
        )
    else:
        result = list_clients(limit=limit, offset=offset, sort=sort)

    return jsonify(result), 200

@bp.get("/<int:client_id>")
def retrieve(client_id: int):
    """Retrieve a single client by ID.
    Path params:
        client_id: Unique client identifier.
    Responses:
        200 OK: Client object (JSON).
        404 Not Found: If no client exists with that ID.
    """
    rec = get_client(client_id)
    return jsonify(rec), 200

@bp.post("/")
def create():
    """Create a new client (ID is user-supplied and must be unique).
    Request body (application/json):
        {
          "id": int,               # required, positive, unique
          "type": "business|...",  # required (enum)
          "name": "...",           # required
          "address_line1": "...",  # optional
          "address_line2": "...",  # optional
          "address_line3": "...",  # optional
          "city": "...",           # optional
          "state": "...",          # optional
          "zip_code": "...",       # optional
          "country": "...",        # required
          "phone_number": "..."    # optional
        }
    Responses:
        201 Created: Created client
        400 Bad Request: Missing/invalid 'id'
        409 Conflict: Duplicate ID.
        422 Any other error
    Notes:
        - The service validates required fields, enum membership, and formats.
    """
    payload = request.get_json(silent=True)
    if payload is None:
        # Force a consistent error when no JSON was provided.
        raise InvalidInput("Request body must be JSON")

    created = create_client(payload)
    # Build a relative Location for the newly created resource.
    location = url_for("clients.retrieve", client_id=created["id"])
    return jsonify(created), 201, {"Location": location}

@bp.put("/<int:client_id>")
def update(client_id: int):
    """Update an existing client. ID is immutable.
    Path params:
        client_id: client ID
    Request body (application/json):
        - Partial or full record.
    Responses:
        200 OK: Updated client JSON.
        400 Bad Request: Body 'id' differs from path id.
        404 Not Found: Client not found.
        422 Any other error
    """
    updates = request.get_json(silent=True) or {}
    updated = update_client(client_id, updates)
    return jsonify(updated), 200

@bp.delete("/<int:client_id>")
def delete(client_id: int):
    """Delete a client by ID.
    Responses:
        204 success
        404 Not Found
    """
    delete_client(client_id)
    return ("", 204)
