"""Small, testable adapter for Databento instrument-definition records.

This module only translates provider record objects into plain mappings.
It does not create a network client, start a live session, or access API keys.
"""
from __future__ import annotations

from collections.abc import Iterable, Iterator, Mapping
from typing import Any

# Fields consumed by InstrumentCatalog. Optional metadata remains optional.
_DEFINITION_FIELDS = (
    "raw_symbol",
    "instrument_id",
    "publisher_id",
    "instrument_class",
    "expiration",
    "currency",
    "min_price_increment",
    "ts_event",
)


class InvalidDatabentoRecord(ValueError):
    """Raised when a DBN definition record cannot be read safely."""


def _normalize_symbol(value: Any) -> str:
    if isinstance(value, bytes):
        try:
            return value.decode("ascii").strip("\x00 ")
        except UnicodeDecodeError as exc:
            raise InvalidDatabentoRecord("Definition symbol is not ASCII.") from exc
    return str(value).strip()


def definition_record_to_mapping(record: Any) -> dict[str, Any]:
    """Extract the stable definition fields from a DBN record-like object.

    Databento DBN records expose fields as attributes. Tests can use simple
    objects with the same attributes, avoiding network calls and credentials.
    """
    try:
        values = {
            field: getattr(record, field)
            for field in _DEFINITION_FIELDS
            if hasattr(record, field)
        }
    except Exception as exc:  # defensive boundary around provider objects
        raise InvalidDatabentoRecord("Could not read definition record.") from exc

    for required in ("raw_symbol", "instrument_id", "publisher_id",
                     "instrument_class", "expiration", "ts_event"):
        if required not in values:
            raise InvalidDatabentoRecord(
                f"Definition record is missing required field: {required}."
            )

    values["raw_symbol"] = _normalize_symbol(values["raw_symbol"])
    return values


def iter_definition_mappings(
    records: Iterable[Any],
) -> Iterator[dict[str, Any]]:
    """Yield normalized mappings while preserving provider record order."""
    for record in records:
        yield definition_record_to_mapping(record)
