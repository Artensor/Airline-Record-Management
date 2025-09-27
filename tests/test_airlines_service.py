import pytest

from src.conf.errors import DuplicateID, ImmutableID, InvalidInput, NotFound
from src.record.airlines.service import (
    create_airline,
    get_airline,
    update_airline,
    delete_airline,
    list_airlines,
    search_airlines,
)
from src.record.airlines.repo import get_repo, _reset_singleton_for_tests


@pytest.fixture(autouse=True)
def _reset_repo(tmp_data_dir):
    # make sure singleton points at this test's DATA_DIR
    _reset_singleton_for_tests()
    yield
    _reset_singleton_for_tests()


def test_create_valid_and_duplicate():
    repo = get_repo()
    a1 = create_airline({"id": 1, "type": "National", "company_name": "Air One"}, repo)
    assert a1["id"] == 1

    with pytest.raises(DuplicateID):
        create_airline({"id": 1, "type": "National", "company_name": "X"}, repo)


def test_missing_id_or_fields():
    repo = get_repo()
    with pytest.raises(InvalidInput):
        create_airline({"type": "National", "company_name": "No ID"}, repo)
    with pytest.raises(InvalidInput):
        create_airline({"id": 2, "type": "bad", "company_name": ""}, repo)


def test_update_id_is_immutable_and_not_found():
    repo = get_repo()
    create_airline({"id": 10, "type": "Charter", "company_name": "CharterCo"}, repo)

    with pytest.raises(ImmutableID):
        update_airline(10, {"id": 11}, repo)

    delete_airline(10, repo)
    with pytest.raises(NotFound):
        get_airline(10, repo)


def test_list_and_search_no_pagination_for_search():
    repo = get_repo()
    create_airline({"id": 1, "type": "National", "company_name": "Air One"}, repo)
    create_airline({"id": 2, "type": "Regional", "company_name": "Sky Two"}, repo)
    create_airline({"id": 3, "type": "National", "company_name": "National Star"}, repo)

    # list with pagination meta
    lst = list_airlines(repo, limit=2, offset=0, sort="id")
    assert lst["count"] == 3 and "limit" in lst and len(lst["data"]) == 2

    # search returns ALL matches (no limit/offset in response)
    res = search_airlines(repo, q="air", sort="company_name")
    assert res["count"] == 1 and "limit" not in res and res["data"][0]["id"] == 1
