from __future__ import annotations
import json, os, tempfile
from pathlib import Path

def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)

def load_list(file_path: Path) -> list[dict]:
    if not file_path.exists():
        ensure_dir(file_path.parent)
        file_path.write_text("[]", encoding="utf-8")
        return []
    raw = file_path.read_text(encoding="utf-8").strip() or "[]"
    data = json.loads(raw)
    return data if isinstance(data, list) else []

def save_list(file_path: Path, data: list[dict]) -> None:
    ensure_dir(file_path.parent)
    fd, tmp = tempfile.mkstemp(dir=str(file_path.parent), prefix=file_path.name, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, file_path)
    finally:
        try:
            if os.path.exists(tmp):
                os.remove(tmp)
        except OSError:
            pass
