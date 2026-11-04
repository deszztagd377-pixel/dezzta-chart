"""Small, testable adapter for Databento instrument-definition records.

This module only translates provider record objects into plain mappings.
It does not create a network client, start a live session, or access API keys.
Provider fixed-point integers are deliberately preserved unchanged; conversion
belongs to the domain adapter that knows each field's documented scale.
"""
from __future__ import annotations

from collections.abc import Iterable, Iterator
from typing import Any

# Keep provider metadata needed for canonical identity, versioned metadata,
# lifecycle processing, and diagnostics. Optional fields remain optional.
_DEFINITION_FIELDS = (
    "raw_symbol",
    "instrument_id",
    "publisher_id",
    "instrument_class",
    "expiration",
    "currency",
    "settl_currency",
    "min_price_increment",
    "display_factor",
    "unit_of_measure_qty",
    "unit_of_measure",
    "contract_multiplier",
    "contract_multiplier_unit",
    "exchange",
    "asset",
    "security_type",
    "security_update_action",
    "activation",
    "min_lot_size",
    "min_lot_size_round_lot",
    "underlying",
    "ts_event",
)

_TEXT_FIELDS = (
    "currency",
    "settl_currency",
    "unit_of_measure",
    "exchange",
    "asset",
    "security_type",
    "security_update_action",
    "underlying",
)


class InvalidDatabentoRecord(ValueError):
    """Raised when a DBN definition record cannot be read safely."""


def _normalize_text(value: Any, field_name: str) -> str:
    if isinstance(value, bytes):
        try:
            return value.decode("ascii").strip("\x00 ")
        except UnicodeDecodeError as exc:
            raise InvalidDatabentoRecord(
                f"Definition {field_name} is not ASCII."
            ) from exc
    return str(value).strip()


def _normalize_symbol(value: Any) -> str:
    return _normalize_text(value, "symbol")


def definition_record_to_mapping(record: Any) -> dict[str, Any]:
    """Extract stable and optional fields from a DBN record-like object.

    DBN character arrays may arrive as bytes; numeric fixed-point fields retain
    their original integer representation so no precision is lost here.
    """
    try:
        values = {
            field: getattr(record, field)
            for field in _DEFINITION_FIELDS
            if hasattr(record, field)
        }
    except Exception as exc:  # defensive boundary around provider objects
        raise InvalidDatabentoRecord("Could not read definition record.") from exc

    for required in (
        "raw_symbol",
        "instrument_id",
        "publisher_id",
        "instrument_class",
        "security_update_action",
        "ts_event",
    ):
        if required not in values:
            raise InvalidDatabentoRecord(
                f"Definition record is missing required field: {required}."
            )

    values["raw_symbol"] = _normalize_symbol(values["raw_symbol"])
    for field in _TEXT_FIELDS:
        if field in values and values[field] is not None:
            values[field] = _normalize_text(values[field], field)

    return values


def iter_definition_mappings(
    records: Iterable[Any],
) -> Iterator[dict[str, Any]]:
    """Yield normalized mappings while preserving provider record order."""
    for record in records:
        yield definition_record_to_mapping(record)
