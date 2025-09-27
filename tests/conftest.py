"""Pytest features for app, temp data dir, and HTTP client.
"""

from __future__ import annotations
import tempfile
from pathlib import Path
import pytest
from flask import Flask
from src.main import create_app
import src.record.clients.repo as clients_repo
import src.record.airlines.repo as airlines_repo

@pytest.fixture(autouse=True)
def reset_clients_repo(tmp_data_dir):
    """Ensure the repo singleton is rebuilt for THIS test's DATA_DIR."""
    if hasattr(clients_repo, "_reset_singleton_for_tests"):
        clients_repo._reset_singleton_for_tests()
    yield
    # Optional: reset again after test to avoid lingering state
    if hasattr(clients_repo, "_reset_singleton_for_tests"):
        clients_repo._reset_singleton_for_tests()

@pytest.fixture(autouse=True)
def _reset_airlines_repo(tmp_data_dir):
    if hasattr(airlines_repo, "_reset_singleton_for_tests"):
        airlines_repo._reset_singleton_for_tests()
    yield
    if hasattr(airlines_repo, "_reset_singleton_for_tests"):
        airlines_repo._reset_singleton_for_tests()

@pytest.fixture()
def tmp_data_dir(monkeypatch):
    """Provide a fresh temporary DATA_DIR for each test."""

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "data"
        path.mkdir(parents=True, exist_ok=True)
        monkeypatch.setenv("DATA_DIR", str(path))
        # AUTOSAVE true so repo writes to disk automatically on each mutation.
        monkeypatch.setenv("AUTOSAVE", "true")
        yield path  # path exists for the lifetime of the test

@pytest.fixture()
def app(tmp_data_dir: Path) -> Flask:
    """Create a Flask app configured for testing."""
    app = create_app()
    app.testing = True
    return app

@pytest.fixture()
def client(app: Flask):
    """Flask HTTP client for API endpoint tests."""
    return app.test_client()

