# ------------------------------------------------------------
# storage.py — Helpers for JSON-backed lists on disk
# ------------------------------------------------------------
from pathlib import Path
import json

def ensure_dir(path: Path) -> None:
    """Create a directory if it doesn't exist."""
    path.mkdir(parents=True, exist_ok=True)

def load_list(file_path: Path) -> list[dict]:
    """Read a JSON list from file, or return [] if missing/empty."""
    if not file_path.exists():
        return []
    try:
        with file_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception:
        # For class project: be forgiving if file is malformed.
        return []

def save_list(file_path: Path, rows: list[dict]) -> None:
    """Write a JSON list to file (pretty for readability)."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)
