"""Domain error classes and HTTP mapping helpers.

Services should raise these exceptions to indicate business/domain errors.
The Flask API layer installs a global error handler that converts them to
consistent JSON error responses.

Error payload shape:
    {
      "error": {
        "code": "<UPPER_SNAKE>",
        "message": "Human-readable text",
        "details": { ... optional context ... }
      }
    }
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Tuple


@dataclass
class DomainError(Exception):
    """Base class for application domain errors.
    Attributes:
        code: Stable machine-readable error code (UPPER_SNAKE_CASE).
        message: Human-readable message safe to show to end users.
        details: Optional free-form payload with context for debugging or UI.
        http_status: HTTP status the API should respond with.
    """
    code: str
    message: str
    details: Any | None = None
    http_status: int = 400

class InvalidID(DomainError):
    """Raised when an ID is missing, not an integer, or non-positive."""
    def __init__(self, message: str = "Invalid ID", details: Any | None = None):
        super().__init__("INVALID_ID", message, details, 400)

class DuplicateID(DomainError):
    """Raised when creating a record with an ID that already exists."""
    def __init__(self, message: str = "ID already exists", details: Any | None = None):
        super().__init__("DUPLICATE_ID", message, details, 409)

class ImmutableID(DomainError):
    """Raised when a request attempts to change an existing record's ID."""
    def __init__(self, message: str = "ID is immutable", details: Any | None = None):
        super().__init__("ID_IMMUTABLE", message, details, 400)

class InvalidInput(DomainError):
    """Raised when input fails validation (non-ID fields)."""
    def __init__(self, message: str = "Invalid input", details: Any | None = None):
        super().__init__("INVALID_INPUT", message, details, 422)

class NotFound(DomainError):
    """Raised when a requested record is not present."""
    def __init__(self, message: str = "Not found", details: Any | None = None):
        super().__init__("NOT_FOUND", message, details, 404)

class FKNotFound(DomainError):
    """Raised when a foreign key reference points to a non-existent record."""
    def __init__(self, message: str = "Related record not found", details: Any | None = None):
        super().__init__("FK_NOT_FOUND", message, details, 422)

def to_http(err: DomainError) -> Tuple[dict, int]:
    """Convert a DomainError to an HTTP response tuple so it can be controlled.
    Args:
        err: A DomainError instance.
    Returns:
        A tuple of (JSON-serializable body, HTTP status code).
    """
    body = {"error": {"code": err.code, "message": err.message}}
    if err.details is not None:
        body["error"]["details"] = err.details
    return body, err.http_status