"""Service-level tests for Clients service."""

from __future__ import annotations
import pytest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.record.clients.repo import ClientsRepo
from src.record.clients.service import (
    create_client,
    get_client,
    update_client,
    delete_client,
    list_clients,
    search_clients,
)
from src.conf.errors import InvalidID, InvalidInput, DuplicateID, ImmutableID, NotFound


def _valid_payload(**overrides):
    """Factory for a minimal valid client payload."""
    base = {
        "id": 1,
        "type": "business",
        "name": "Alice",
        "address_line1": "123 Ave",
        "city": "San José",
        "state": "SJ",
        "zip_code": "10101",
        "country": "CR",
        "phone_number": "+506 8888-8888",
    }
    base.update(overrides)
    return base


def test_create_valid_and_duplicate(tmp_data_dir: Path):
    repo = ClientsRepo(tmp_data_dir)

    created = create_client(_valid_payload(), repo=repo)
    assert created["id"] == 1
    assert repo.get_by_id(1) is not None

    # Duplicate ID should raise DuplicateID (409 at the API layer).
    with pytest.raises(DuplicateID):
        create_client(_valid_payload(), repo=repo)


def test_missing_id_yields_invalid_input(tmp_data_dir: Path):
    """Missing 'id' is treated as missing required field → InvalidInput."""
    repo = ClientsRepo(tmp_data_dir)

    payload = _valid_payload()
    payload.pop("id")
    with pytest.raises(InvalidInput):
        create_client(payload, repo=repo)


def test_invalid_id_non_int_or_non_positive(tmp_data_dir: Path):
    repo = ClientsRepo(tmp_data_dir)

    with pytest.raises(InvalidID):
        create_client(_valid_payload(id="abc"), repo=repo)

    with pytest.raises(InvalidID):
        create_client(_valid_payload(id=0), repo=repo)

    with pytest.raises(InvalidID):
        create_client(_valid_payload(id=-5), repo=repo)


def test_invalid_enum_and_formats(tmp_data_dir: Path):
    repo = ClientsRepo(tmp_data_dir)

    with pytest.raises(InvalidInput):
        create_client(_valid_payload(type="unknown"), repo=repo)

    with pytest.raises(InvalidInput):
        create_client(_valid_payload(phone_number="not-a-phone"), repo=repo)

    with pytest.raises(InvalidInput):
        create_client(_valid_payload(zip_code="@!"), repo=repo)


def test_update_id_is_immutable(tmp_data_dir: Path):
    repo = ClientsRepo(tmp_data_dir)
    create_client(_valid_payload(id=7), repo=repo)

    # Body id mismatching path triggers ImmutableID.
    with pytest.raises(ImmutableID):
        update_client(7, {"id": 8}, repo=repo)


def test_update_and_get_and_delete_flow(tmp_data_dir: Path):
    repo = ClientsRepo(tmp_data_dir)
    create_client(_valid_payload(id=10, name="Alice"), repo=repo)

    updated = update_client(10, {"city": "Heredia"}, repo=repo)
    assert updated["city"] == "Heredia"

    fetched = get_client(10, repo=repo)
    assert fetched["name"] == "Alice"

    # Delete then ensure NotFound is raised on second delete/get.
    delete_client(10, repo=repo)
    with pytest.raises(NotFound):
        get_client(10, repo=repo)


def test_list_and_search_pagination_and_sort(tmp_data_dir: Path):
    repo = ClientsRepo(tmp_data_dir)
    # Seed three records
    create_client(_valid_payload(id=1, name="Zeta", city="Alajuela"), repo=repo)
    create_client(_valid_payload(id=2, name="Beta", city="San José"), repo=repo)
    create_client(_valid_payload(id=3, name="Alpha", city="Heredia"), repo=repo)

    # list default sort by id asc
    env = list_clients(repo=repo)
    assert [r["id"] for r in env["data"]] == [1, 2, 3]

    # sort by name asc
    env2 = list_clients(repo=repo, sort="name")
    assert [r["name"] for r in env2["data"]] == ["Alpha", "Beta", "Zeta"]

    # pagination limit/offset
    env3 = list_clients(repo=repo, limit=2, offset=1, sort="id")
    assert [r["id"] for r in env3["data"]] == [2, 3]

    # search by q across name/city/etc.
    s1 = search_clients(repo=repo, q="her")  # matches "Heredia"
    assert [r["city"] for r in s1["data"]] == ["Heredia"]

    # exact filter by city (case-insensitive)
    s2 = search_clients(repo=repo, city="san josé")
    assert [r["id"] for r in s2["data"]] == [2]
