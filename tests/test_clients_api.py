"""API-level tests for /api/v1/clients endpoints.

We assert:
- 201 on create with Location header
- 409 on duplicate id
- 400/422 error shapes on invalid input
- 200 on get/list/search/update
- 204 on delete
"""

from __future__ import annotations
import json
import pytest
from flask import Flask

def _post_json(client, url: str, payload: dict):
    return client.post(url, data=json.dumps(payload), content_type="application/json")

BASE = "/api/v1/clients"

def test_create_then_get(client):
    # Create
    resp = _post_json(client, BASE, {
        "id": 1, "type": "business", "name": "Alice",
        "address_line1": "123 Ave", "city": "San José",
        "state": "SJ", "zip_code": "10101", "country": "CR",
        "phone_number": "+506 8888-8888"
    })
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["id"] == 1
    assert "Location" in resp.headers

    # Retrieve
    r2 = client.get(f"{BASE}/1")
    assert r2.status_code == 200
    assert r2.get_json()["name"] == "Alice"


def test_duplicate_id_code_409(client):
    payload = {
        "id": 2, "type": "business", "name": "Bob",
        "address_line1": "Main", "city": "Heredia", "state": "HJ",
        "zip_code": "20101", "country": "CR", "phone_number": "+506 7777-7777"
    }
    r1 = _post_json(client, BASE, payload)
    assert r1.status_code == 201

    r2 = _post_json(client, BASE, payload)
    assert r2.status_code == 409
    err = r2.get_json()["error"]
    assert err["code"] == "DUPLICATE_ID"


def test_missing_body_json_code_422(client):
    r = client.post(BASE, data="not-json", content_type="text/plain")
    assert r.status_code == 422
    err = r.get_json()["error"]
    assert err["code"] == "INVALID_INPUT"


def test_put_id_mismatch_code_400(client):
    # Seed
    _post_json(client, BASE, {
        "id": 3, "type": "business", "name": "Carol",
        "address_line1": "Street", "city": "Alajuela", "state": "AJ",
        "zip_code": "30101", "country": "CR", "phone_number": "+506 6666-6666"
    })

    # Mismatch id in body vs path
    r = client.put(f"{BASE}/3", data=json.dumps({"id": 9}), content_type="application/json")
    assert r.status_code == 400
    assert r.get_json()["error"]["code"] == "ID_IMMUTABLE"


def test_update_and_delete_flow(client):
    # Seed
    _post_json(client, BASE, {
        "id": 4, "type": "business", "name": "Dave",
        "address_line1": "Ave", "city": "Cartago", "state": "CA",
        "zip_code": "40101", "country": "CR", "phone_number": "+506 5555-5555"
    })

    # Update
    r = client.put(f"{BASE}/4", data=json.dumps({"city": "Puntarenas"}), content_type="application/json")
    assert r.status_code == 200
    assert r.get_json()["city"] == "Puntarenas"

    # List/search
    rlist = client.get(f"{BASE}?q=punt")
    assert rlist.status_code == 200
    assert rlist.get_json()["count"] == 1

    # Delete
    rdel = client.delete(f"{BASE}/4")
    assert rdel.status_code == 204

    # Verify gone
    rget = client.get(f"{BASE}/4")
    assert rget.status_code == 404
