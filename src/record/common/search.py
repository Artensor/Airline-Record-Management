"""Search utilities for simple case-insensitive substring matching."""

from __future__ import annotations
from typing import Iterable, Mapping, Any, List

def to_lowercase(value: Any) -> str:
    """Normalize any value to a lowercase string for comparison."""
    return str(value or "").lower()

def matches_any_fields(record: Mapping[str, Any], fields: List[str], q: str) -> bool:
    """Check if a record matches a query across any of the provided fields.
    Args:
        record: Mapping of the record (dict-like).
        fields: List of field names to search.
    Returns:
        True if any field contains the query (case-insensitive), else False.
    """
    qn = to_lowercase(q)
    return any(qn in to_lowercase(record.get(f)) for f in fields)

def filter_by_q(items: Iterable[Mapping[str, Any]], fields: List[str], q: str) -> list[Mapping[str, Any]]:
    """Return items whose selected fields contain the query string.
    Args:
        items: Iterable of dict-like records.
        fields: Fields to include in search.

    Returns:
        A list of records that match, preserving the input order.
    """
    q = (q or "").strip()
    if not q:
        return list(items)
    return [r for r in items if matches_any_fields(r, fields, q)]