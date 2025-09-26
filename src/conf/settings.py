from __future__ import annotations
from pathlib import Path

# Path to /src
SRC_ROOT = Path(__file__).resolve().parents[1]
# Default data dir inside the repo (portable after unzip)
DATA_DIR = SRC_ROOT / "data"

TIMEZONE = "Europe/London"
API_VERSION = "v1"
AUTOSAVE = True