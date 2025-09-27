from __future__ import annotations

from flask import Blueprint, jsonify, request, url_for

from src.conf.errors import InvalidInput
from src.record.airlines.service import (
    create_airline,
    get_airline,
    update_airline,
    delete_airline,
    list_airlines,
    search_airlines,
    DEFAULT_LIMIT,
)

bp = Blueprint("airlines", __name__)

@bp.get("/")
def list_or_search():
    """
    GET /api/v1/airlines
    - If search params present (q or type): return ALL matches.
    - Otherwise: paginated list (limit/offset) like Clients.
    """
    args = request.args
    q = args.get("q")
    f_type = args.get("type")
    sort = args.get("sort", default="id", type=str)

    if any([q, f_type]):
        result = search_airlines(q=q or "", type=f_type, sort=sort)
        return jsonify(result), 200

    limit = args.get("limit", default=DEFAULT_LIMIT, type=int)
    offset = args.get("offset", default=0, type=int)
    result = list_airlines(limit=limit, offset=offset, sort=sort)
    return jsonify(result), 200

@bp.get("/<int:airline_id>")
def retrieve(airline_id: int):
    return jsonify(get_airline(airline_id)), 200

@bp.post("/")
def create():
    payload = request.get_json(silent=True)
    if payload is None:
        raise InvalidInput("Request body must be JSON")
    created = create_airline(payload)
    return jsonify(created), 201, {"Location": url_for("airlines.retrieve", airline_id=created["id"])}

@bp.put("/<int:airline_id>")
def update(airline_id: int):
    updates = request.get_json(silent=True) or {}
    return jsonify(update_airline(airline_id, updates)), 200

@bp.delete("/<int:airline_id>")
def delete(airline_id: int):
    delete_airline(airline_id)
    return ("", 204)
