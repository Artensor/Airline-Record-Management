# ------------------------------------------------------------
# errors.py — Small custom exception types for API mapping
# ------------------------------------------------------------

class InvalidInput(Exception):
    """Raised when the provided input/body fails validation (HTTP 422)."""

class InvalidID(Exception):
    """Raised when an ID is missing, not an int, or not positive (HTTP 400)."""

class DuplicateID(Exception):
    """Raised when creating a record with an ID that already exists (HTTP 409)."""

class NotFound(Exception):
    """Raised when a requested record does not exist (HTTP 404)."""

class ImmutableID(Exception):
    """Raised when a caller tries to change an immutable identity field (HTTP 400)."""
