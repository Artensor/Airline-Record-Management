# ------------------------------------------------------------
# repo.py (flights) — JSON-backed list with composite identity
# ------------------------------------------------------------
from __future__ import annotations
import os
from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping, Optional
from src.conf import settings
from src.conf.errors import NotFound
from src.record.common.storage import ensure_dir, load_list, save_list
# Create Flights class
class FlightsRepo:
    FILE_NAME = "flights.json"
    # Initialize the class
    def __init__(self, data_dir: Optional[Path | str] = None, autosave: Optional[bool] = None) -> None:
        base = Path(os.getenv("DATA_DIR", data_dir or settings.DATA_DIR))
        ensure_dir(base)
        self._file_path: Path = base / self.FILE_NAME
        self._autosave: bool = settings.AUTOSAVE if autosave is None else bool(autosave)
        self._loaded: bool = False
        self._flights: list[dict] = []
    # Ensure data is loaded from file
    def _ensure_loaded(self) -> None:
        if not self._loaded:
            self._flights = load_list(self._file_path)
            self._loaded = True
    # Save data to file
    def save(self) -> None:
        self._ensure_loaded()
        save_list(self._file_path, self._flights)
    # Reload data from file
    def reload(self) -> None:
        self._flights = load_list(self._file_path)
        self._loaded = True
    # List all flights
    def list_all(self) -> list[dict]:
        """Return all flight rows (deep copy)."""
        self._ensure_loaded()
        return [deepcopy(r) for r in self._flights]
    # Get flight by composite key
    def get_one(self, client_id: int, airline_id: int, date: str) -> dict:
        """Find a single flight by (client_id, airline_id, date) or raise NotFound."""
        self._ensure_loaded()
        for r in self._flights:
            if (
                int(r.get("client_id", -1)) == int(client_id)
                and int(r.get("airline_id", -1)) == int(airline_id)
                and r.get("date") == date
            ):
                return deepcopy(r)
        raise NotFound(f"Flight with client_id={client_id}, airline_id={airline_id}, date={date} not found")
    # Insert a new flight
    def insert(self, record: Mapping[str, Any]) -> dict:
        self._ensure_loaded()
        rec = dict(record)
        self._flights.append(rec)
        if self._autosave:
            self.save()
        return deepcopy(rec)
    # Update an existing flight
    def update(self, client_id: int, airline_id: int, date: str, patch: Mapping[str, Any]) -> dict:
        self._ensure_loaded()
        for i, rec in enumerate(self._flights):
            if (
                int(rec.get("client_id", -1)) == int(client_id)
                and int(rec.get("airline_id", -1)) == int(airline_id)
                and rec.get("date") == date
            ):
                updated = dict(rec)
                updated.update(patch)
                self._flights[i] = updated
                if self._autosave:
                    self.save()
                return deepcopy(updated)
        raise NotFound(f"Flight with client_id={client_id}, airline_id={airline_id}, date={date} not found")
    # Delete a flight by composite key
    def delete(self, client_id: int, airline_id: int, date: str) -> bool:
        self._ensure_loaded()
        for i, rec in enumerate(self._flights):
            if (
                int(rec.get("client_id", -1)) == int(client_id)
                and int(rec.get("airline_id", -1)) == int(airline_id)
                and rec.get("date") == date
            ):
                del self._flights[i]
                if self._autosave:
                    self.save()
                return True
        return False

    @property
    def path(self) -> Path:
        return self._file_path

_repo_singleton: Optional[FlightsRepo] = None
_repo_dir: Optional[Path | str] = None
# Singleton accessor
def get_repo() -> FlightsRepo:
    """Env-aware singleton repo (helpful for tests)."""
    global _repo_singleton, _repo_dir
    desired = Path(os.getenv("DATA_DIR", settings.DATA_DIR))
    if _repo_singleton is None or _repo_dir != desired:
        _repo_singleton = FlightsRepo(desired)
        _repo_dir = desired
    return _repo_singleton
# Save all changes if autosave is enabled
def save_all() -> None:
    if _repo_singleton is not None:
        _repo_singleton.save()

def _reset_singleton_for_tests() -> None:
    global _repo_singleton, _repo_dir
    _repo_singleton = None
    _repo_dir = None
