import pytest

from src.main import create_app

@pytest.fixture()
def client():
    app = create_app()
    app.config.update(TESTING=True)
    return app.test_client()

def test_create_then_get(client):
    # create
    r = client.post("/api/v1/airlines", json={"id": 1, "type": "National", "company_name": "Air One"})
    assert r.status_code == 201
    # get
    r = client.get("/api/v1/airlines/1")
    assert r.status_code == 200
    assert r.get_json()["company_name"] == "Air One"

def test_duplicate_and_validation(client):
    client.post("/api/v1/airlines", json={"id": 1, "type": "National", "company_name": "Air One"})
    r = client.post("/api/v1/airlines", json={"id": 1, "type": "National", "company_name": "X"})
    assert r.status_code == 409

    r = client.post("/api/v1/airlines", json={"id": 2, "type": "bad", "company_name": ""})
    assert r.status_code in (422, 400)

def test_update_and_delete_flow(client):
    client.post("/api/v1/airlines", json={"id": 5, "type": "Regional", "company_name": "Sky Two"})
    r = client.put("/api/v1/airlines/5", json={"company_name": "Sky 2"})
    assert r.status_code == 200
    assert r.get_json()["company_name"] == "Sky 2"

    r = client.delete("/api/v1/airlines/5")
    assert r.status_code == 204
    r = client.get("/api/v1/airlines/5")
    assert r.status_code == 404

def test_list_and_search(client):
    client.post("/api/v1/airlines", json={"id": 1, "type": "National", "company_name": "Air One"})
    client.post("/api/v1/airlines", json={"id": 2, "type": "Regional", "company_name": "Sky Two"})
    client.post("/api/v1/airlines", json={"id": 3, "type": "National", "company_name": "National Star"})

    # list (keeps pagination)
    r = client.get("/api/v1/airlines?limit=2&offset=0&sort=id")
    body = r.get_json()
    assert r.status_code == 200
    assert body["count"] == 3 and "limit" in body and len(body["data"]) == 2

    # search (NO pagination): returns all matches, no limit/offset in payload
    r = client.get("/api/v1/airlines?q=na&type=National&sort=company_name")
    body = r.get_json()
    assert r.status_code == 200
    assert "limit" not in body and "offset" not in body
    assert body["count"] == 2
    assert [x["id"] for x in body["data"]] == [1, 3]  # ascending by company_name
