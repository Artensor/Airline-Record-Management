from __future__ import annotations

import os
from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping, Optional

from src.conf import settings
from src.conf.errors import NotFound
from src.record.common.storage import ensure_dir, load_list, save_list

class AirlinesRepo:
    """
    Tiny JSON-backed store for airlines.
    File: airlines.json under DATA_DIR.
    """

    FILE_NAME = "airlines.json"

    def __init__(self, data_dir: Optional[Path | str] = None, autosave: Optional[bool] = None) -> None:
        base = Path(os.getenv("DATA_DIR", data_dir or settings.DATA_DIR))
        ensure_dir(base)
        self._file_path: Path = base / self.FILE_NAME
        self._autosave: bool = settings.AUTOSAVE if autosave is None else bool(autosave)
        self._loaded = False
        self._rows: list[dict] = []

    def _ensure_loaded(self) -> None:
        if not self._loaded:
            self._rows = load_list(self._file_path)
            self._loaded = True

    def save(self) -> None:
        self._ensure_loaded()
        save_list(self._file_path, self._rows)

    def reload(self) -> None:
        self._rows = load_list(self._file_path)
        self._loaded = True

    def list_all(self) -> list[dict]:
        self._ensure_loaded()
        return list(self._rows)

    def get_by_id(self, airline_id: int) -> dict | None:
        self._ensure_loaded()
        for rec in self._rows:
            if int(rec.get("id", -1)) == int(airline_id):
                return deepcopy(rec)
        return None

    def exists(self, airline_id: int) -> bool:
        return self.get_by_id(airline_id) is not None

    def insert(self, record: Mapping[str, Any]) -> dict:
        self._ensure_loaded()
        rec = dict(record)
        self._rows.append(rec)
        if self._autosave:
            self.save()
        return deepcopy(rec)

    def update(self, airline_id: int, patch: Mapping[str, Any]) -> dict:
        self._ensure_loaded()
        for i, rec in enumerate(self._rows):
            if int(rec.get("id", -1)) == int(airline_id):
                new_rec = {**rec, **{k: v for k, v in patch.items() if k != "id"}}
                self._rows[i] = new_rec
                if self._autosave:
                    self.save()
                return deepcopy(new_rec)
        raise NotFound(f"Airline {airline_id} not found")

    def delete(self, airline_id: int) -> bool:
        self._ensure_loaded()
        for i, rec in enumerate(self._rows):
            if int(rec.get("id", -1)) == int(airline_id):
                del self._rows[i]
                if self._autosave:
                    self.save()
                return True
        return False

    @property
    def file_path(self) -> Path:
        return self._file_path


# Lazy, env-aware singleton
_repo_singleton: Optional[AirlinesRepo] = None
_repo_dir: Optional[Path] = None

def get_repo() -> AirlinesRepo:
    global _repo_singleton, _repo_dir
    desired = Path(os.getenv("DATA_DIR", settings.DATA_DIR))
    if _repo_singleton is None or _repo_dir != desired:
        _repo_singleton = AirlinesRepo(desired)
        _repo_dir = desired
    return _repo_singleton

def save_all() -> None:
    if _repo_singleton is not None:
        _repo_singleton.save()

# Used by tests to isolate state
def _reset_singleton_for_tests() -> None:
    global _repo_singleton, _repo_dir
    _repo_singleton = None
    _repo_dir = None
