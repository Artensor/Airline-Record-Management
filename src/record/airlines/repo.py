# ------------------------------------------------------------
# repo.py (airlines) — JSON-backed list with simple CRUD
# ------------------------------------------------------------
from __future__ import annotations
import os
from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping, Optional
from src.conf import settings
from src.conf.errors import NotFound
from src.record.common.storage import ensure_dir, load_list, save_list

class AirlinesRepo:
    FILE_NAME = "airlines.json"

    #Initiate the repository, loading data from the specified directory or environment variable.
    def __init__(self, data_dir: Optional[Path | str] = None, autosave: Optional[bool] = None) -> None:
        base = Path(os.getenv("DATA_DIR", data_dir or settings.DATA_DIR))
        ensure_dir(base)
        self._file_path: Path = base / self.FILE_NAME
        self._autosave: bool = settings.AUTOSAVE if autosave is None else bool(autosave)
        self._loaded: bool = False
        self._airlines: list[dict] = []

    #Ensure the data is loaded from the file if it hasn't been already.
    def _ensure_loaded(self) -> None:
        if not self._loaded:
            self._airlines = load_list(self._file_path)
            self._loaded = True
    #Save the current state of the data to the file.
    def save(self) -> None:
        self._ensure_loaded()
        save_list(self._file_path, self._airlines)
    #Reload the data from the file, discarding any unsaved changes.
    def reload(self) -> None:
        self._airlines = load_list(self._file_path)
        self._loaded = True
    #List all airline records.
    def list_all(self) -> list[dict]:
        self._ensure_loaded()
        return [deepcopy(r) for r in self._airlines]
    #Get a specific airline record by its ID.
    def get_by_id(self, airline_id: int) -> dict:
        self._ensure_loaded()
        for r in self._airlines:
            if int(r.get("id", -1)) == int(airline_id):
                return deepcopy(r)
        from src.conf.errors import NotFound
        raise NotFound(f"Airline {airline_id} not found")
    #Insert a new airline record.
    def insert(self, record: Mapping[str, Any]) -> dict:
        self._ensure_loaded()
        rec = dict(record)
        self._airlines.append(rec)
        if self._autosave:
            self.save()
        return deepcopy(rec)
    #Update an existing airline record by its ID.
    def update(self, airline_id: int, patch: Mapping[str, Any]) -> dict:
        self._ensure_loaded()
        for i, rec in enumerate(self._airlines):
            if int(rec.get("id", -1)) == int(airline_id):
                updated = dict(rec)
                updated.update(patch)
                self._airlines[i] = updated
                if self._autosave:
                    self.save()
                return deepcopy(updated)
        raise NotFound(f"Airline {airline_id} not found")
    #Delete an airline record by its ID.
    def delete(self, airline_id: int) -> bool:
        self._ensure_loaded()
        for i, rec in enumerate(self._airlines):
            if int(rec.get("id", -1)) == int(airline_id):
                del self._airlines[i]
                if self._autosave:
                    self.save()
                return True
        return False

    @property
    def path(self) -> Path:
        return self._file_path

_repo_singleton: Optional[AirlinesRepo] = None
_repo_dir: Optional[Path | str] = None

# Get the singleton instance of the AirlinesRepo, creating it if necessary.
def get_repo() -> AirlinesRepo:
    global _repo_singleton, _repo_dir
    desired = Path(os.getenv("DATA_DIR", settings.DATA_DIR))
    if _repo_singleton is None or _repo_dir != desired:
        _repo_singleton = AirlinesRepo(desired)
        _repo_dir = desired
    return _repo_singleton
# Save the current state of the singleton repository if it exists.
def save_all() -> None:
    if _repo_singleton is not None:
        _repo_singleton.save()
# Reset the singleton repository for testing purposes.
def _reset_singleton_for_tests() -> None:
    global _repo_singleton, _repo_dir
    _repo_singleton = None
    _repo_dir = None
