from __future__ import annotations
import os
from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping, Optional
from src.conf import settings
from src.conf.errors import NotFound
from src.record.common.storage import ensure_dir, load_list, save_list

class ClientsRepo:
    """JSON-backed list of clients with simple CRUD."""
    FILE_NAME = "clients.json"

    def __init__(self, data_dir: Optional[Path | str] = None, autosave: Optional[bool] = None) -> None:
        base = Path(os.getenv("DATA_DIR", data_dir or settings.DATA_DIR))
        ensure_dir(base)
        self._file_path: Path = base / self.FILE_NAME
        self._autosave: bool = settings.AUTOSAVE if autosave is None else bool(autosave)
        self._loaded: bool = False
        self._clients: list[dict] = []

    def _ensure_loaded(self) -> None:
        if not self._loaded:
            self._clients = load_list(self._file_path)
            self._loaded = True

    def save(self) -> None:
        self._ensure_loaded()
        save_list(self._file_path, self._clients)

    def reload(self) -> None:
        self._clients = load_list(self._file_path)
        self._loaded = True

    def list_all(self) -> list[dict]:
        self._ensure_loaded()
        return list(self._clients)

    def get_by_id(self, client_id: int) -> dict | None:
        self._ensure_loaded()
        for rec in self._clients:
            if int(rec.get("id", -1)) == int(client_id):
                return deepcopy(rec)
        return None

    def exists(self, client_id: int) -> bool:
        return self.get_by_id(client_id) is not None

    def insert(self, record: Mapping[str, Any]) -> dict:
        self._ensure_loaded()
        rec = dict(record)
        self._clients.append(rec)
        if self._autosave:
            self.save()
        return deepcopy(rec)

    def update(self, client_id: int, patch: Mapping[str, Any]) -> dict:
        self._ensure_loaded()
        for i, rec in enumerate(self._clients):
            if int(rec.get("id", -1)) == int(client_id):
                new_rec = {**rec, **{k: v for k, v in patch.items() if k != "id"}}
                self._clients[i] = new_rec
                if self._autosave:
                    self.save()
                return deepcopy(new_rec)
        raise NotFound(f"Client {client_id} not found")

    def delete(self, client_id: int) -> bool:
        self._ensure_loaded()
        for i, rec in enumerate(self._clients):
            if int(rec.get("id", -1)) == int(client_id):
                del self._clients[i]
                if self._autosave:
                    self.save()
                return True
        return False

    @property
    def file_path(self) -> Path:
        return self._file_path

# Lazy, env-aware singleton
_repo_singleton: Optional[ClientsRepo] = None
_repo_dir: Optional[Path] = None

def get_repo() -> ClientsRepo:
    global _repo_singleton, _repo_dir
    desired = Path(os.getenv("DATA_DIR", settings.DATA_DIR))
    if _repo_singleton is None or _repo_dir != desired:
        _repo_singleton = ClientsRepo(desired)
        _repo_dir = desired
    return _repo_singleton

def save_all() -> None:
    if _repo_singleton is not None:
        _repo_singleton.save()

def _reset_singleton_for_tests() -> None:
    global _repo_singleton, _repo_dir
    _repo_singleton = None
    _repo_dir = None
