# ------------------------------------------------------------
# settings.py — Small project settings with sensible defaults
# ------------------------------------------------------------
from pathlib import Path
import os

# Data directory where JSON files live. Overridable via DATA_DIR env.
DATA_DIR = Path(os.getenv("DATA_DIR", "./data")).resolve()

# Autosave turns on immediate writes after each change.
AUTOSAVE = True
