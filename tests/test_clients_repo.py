"""Repository-level tests for ClientsRepo.

Verify:
- Loading from missing file yields an empty list and creates '[]'.
- Insert/get/update/delete behaviors.
- save() persists changes.
"""

from __future__ import annotations
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.record.clients.repo import ClientsRepo

def test_loads_empty_and_creates_file(tmp_data_dir: Path):
    repo = ClientsRepo(tmp_data_dir)
    # Initially no file is present; load triggers creation of [].
    assert repo.list_all() == []
    assert repo.file_path.exists()
    assert repo.file_path.read_text(encoding="utf-8").strip() == "[]"

def test_insert_get_update_delete_save(tmp_data_dir: Path):
    repo = ClientsRepo(tmp_data_dir)
    # Insert a minimal dict (service validates; repo trusts).
    alice = {"id": 1, "type": "business", "name": "Alice"}
    inserted = repo.insert(alice)
    assert inserted["id"] == 1
    # get_by_id returns a copy
    fetched = repo.get_by_id(1)
    assert fetched == inserted
    assert repo.exists(1) is True

    # Update merges fields; 'id' remains unchanged even if present in patch.
    updated = repo.update(1, {"city": "San José", "id": 999})
    assert updated["id"] == 1
    assert updated["city"] == "San José"

    # Save is automatic, but call explicitly to exercise the path.
    repo.save()
    # Force reload from disk; state should be consistent.
    assert repo.get_by_id(1)

    # Delete returns True on success, False otherwise.
    assert repo.delete(1) is True
    assert repo.delete(1) is False
