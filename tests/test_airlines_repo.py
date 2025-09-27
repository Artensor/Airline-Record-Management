from pathlib import Path

from src.record.airlines.repo import AirlinesRepo

def test_insert_get_update_delete_roundtrip(tmp_path: Path):
    repo = AirlinesRepo(tmp_path, autosave=True)

    # insert
    a = repo.insert({"id": 1, "type": "national", "company_name": "Air One"})
    assert a["id"] == 1

    # get
    got = repo.get_by_id(1)
    assert got and got["company_name"] == "Air One"

    # update
    upd = repo.update(1, {"company_name": "Air Uno"})
    assert upd["company_name"] == "Air Uno"

    # delete
    assert repo.delete(1) is True
    assert repo.get_by_id(1) is None

def test_persistence_roundtrip(tmp_path: Path):
    repo = AirlinesRepo(tmp_path, autosave=True)
    repo.insert({"id": 2, "type": "regional", "company_name": "Sky Reg"})
    repo.save()

    repo2 = AirlinesRepo(tmp_path, autosave=False)
    result = repo2.get_by_id(2)
    assert result is not None
    assert result["company_name"] == "Sky Reg"
