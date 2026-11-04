"""Strict, lossless normalization of Databento instrument definitions.

This adapter intentionally supports only dated futures in the initial CME
scope. It does not infer a root from a ticker, invent missing venue/currency,
or convert DBN fixed-point integers into decimal floats.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Mapping
from uuid import UUID

from app.instrument_identity import CanonicalInstrument

_NS_PER_SECOND = 1_000_000_000
_NS_PER_MICROSECOND = 1_000
_SQLITE_MAX_INTEGER = 9_223_372_036_854_775_807
_SUPPORTED_FUTURES_CLASS = "F"


class InvalidDatabentoDefinition(ValueError):
    """The provider definition lacks authoritative fields or is ambiguous."""


@dataclass(frozen=True, slots=True)
class NormalizedDatabentoDefinition:
    action: str
    provider: str
    dataset: str
    publisher_id: int
    instrument_id: int
    raw_symbol: str
    source_event_ts_ns: int
    instrument: CanonicalInstrument | None
    metadata: dict[str, Any]


def _text(row: Mapping[str, Any], field: str, *, required: bool = True) -> str | None:
    value = row.get(field)
    if value is None:
        if required:
            raise InvalidDatabentoDefinition(f"missing_authoritative_{field}")
        return None
    if not isinstance(value, str) or not value.strip():
        if required:
            raise InvalidDatabentoDefinition(f"missing_authoritative_{field}")
        return None
    return value.strip()


def _integer(row: Mapping[str, Any], field: str, *, minimum: int = 0) -> int:
    value = row.get(field)
    if not isinstance(value, int) or isinstance(value, bool) or value < minimum:
        raise InvalidDatabentoDefinition(f"invalid_{field}")
    if value > _SQLITE_MAX_INTEGER:
        raise InvalidDatabentoDefinition(f"out_of_range_{field}")
    return value


def _expiration_date(expiration_ns: int) -> str:
    # Avoid float timestamps: conversion is integer-only and deterministic.
    seconds, nanos = divmod(expiration_ns, _NS_PER_SECOND)
    micros = nanos // _NS_PER_MICROSECOND
    try:
        instant = datetime(1970, 1, 1, tzinfo=timezone.utc) + timedelta(
            seconds=seconds, microseconds=micros
        )
    except OverflowError:
        raise InvalidDatabentoDefinition("invalid_expiration_timestamp") from None
    return instant.date().isoformat()


def normalize_databento_definition(
    row: Mapping[str, Any],
    *,
    canonical_id: str | None,
    dataset: str,
    provider: str = "databento",
) -> NormalizedDatabentoDefinition:
    """Validate a provider definition and preserve all contract terms losslessly.

    canonical_id is supplied only after an existing provider mapping has been
    resolved or a registry-issued UUID has been allocated.
    """
    if not isinstance(row, Mapping):
        raise TypeError("row must be a mapping.")
    if not isinstance(dataset, str) or not dataset.strip():
        raise ValueError("dataset is required.")
    if not isinstance(provider, str) or not provider.strip():
        raise ValueError("provider is required.")

    action = _text(row, "security_update_action").upper()
    if action not in {"A", "M", "D"}:
        raise InvalidDatabentoDefinition("unsupported_security_update_action")
    raw_symbol = _text(row, "raw_symbol").upper()
    publisher_id = _integer(row, "publisher_id", minimum=1)
    instrument_id = _integer(row, "instrument_id", minimum=1)
    source_event_ts_ns = _integer(row, "ts_event")

    if action == "D":
        return NormalizedDatabentoDefinition(
            action=action,
            provider=provider.strip().lower(),
            dataset=dataset.strip().upper(),
            publisher_id=publisher_id,
            instrument_id=instrument_id,
            raw_symbol=raw_symbol,
            source_event_ts_ns=source_event_ts_ns,
            instrument=None,
            metadata={"raw_symbol": raw_symbol, "security_update_action": action},
        )

    instrument_class = _text(row, "instrument_class").upper()
    if instrument_class != _SUPPORTED_FUTURES_CLASS:
        raise InvalidDatabentoDefinition("unsupported_instrument_class")
    root = _text(row, "asset").upper()
    venue = _text(row, "exchange").upper()
    currency = _text(row, "currency").upper()
    # Databento defines settl_currency as an override when settlement differs
    # from currency. An absent override therefore means currency.
    settlement_currency = (_text(row, "settl_currency", required=False) or currency).upper()
    expiration_ns = _integer(row, "expiration", minimum=1)
    expiration = _expiration_date(expiration_ns)

    normalized_id: str | None = None
    if canonical_id is not None:
        try:
            normalized_id = str(UUID(canonical_id))
        except (ValueError, TypeError, AttributeError):
            raise ValueError("canonical_id must be a registry-issued UUID.") from None

    instrument = None
    if normalized_id is not None:
        instrument = CanonicalInstrument(
            canonical_id=normalized_id,
            asset_class="future",
            instrument_type="future",
            symbol=root,
            venue=venue,
            name=raw_symbol,
            settlement_currency=settlement_currency,
            expiration_date=expiration,
        )

    # Keep DBN fixed-point integers and their scales explicit. In particular,
    # do not equate unit_of_measure_qty with contract_multiplier.
    metadata: dict[str, Any] = {
        "metadata_schema_version": 1,
        "provider": provider.strip().lower(),
        "dataset": dataset.strip().upper(),
        "raw_symbol": raw_symbol,
        "instrument_class": instrument_class,
        "asset_root": root,
        "exchange": venue,
        "expiration_ns": expiration_ns,
        "expiration_date_utc": expiration,
        "currency": currency,
        "settlement_currency": settlement_currency,
        "settl_currency_override": row.get("settl_currency"),
        "min_price_increment_raw": row.get("min_price_increment"),
        "min_price_increment_scale": 1_000_000_000,
        "display_factor_raw": row.get("display_factor"),
        "unit_of_measure_qty_raw": row.get("unit_of_measure_qty"),
        "unit_of_measure_qty_scale": 1_000_000_000,
        "unit_of_measure": row.get("unit_of_measure"),
        "contract_multiplier_raw": row.get("contract_multiplier"),
        "contract_multiplier_encoding": "provider_native_integer",
        "contract_multiplier_unit": row.get("contract_multiplier_unit"),
        "min_lot_size_raw": row.get("min_lot_size"),
        "min_lot_size_scale": 1_000_000_000,
        "min_lot_size_round_lot_raw": row.get("min_lot_size_round_lot"),
        "min_lot_size_round_lot_scale": 1_000_000_000,
        "activation_ns": row.get("activation"),
        "source_event_ts_ns": source_event_ts_ns,
        "security_update_action": action,
    }
    return NormalizedDatabentoDefinition(
        action=action,
        provider=provider.strip().lower(),
        dataset=dataset.strip().upper(),
        publisher_id=publisher_id,
        instrument_id=instrument_id,
        raw_symbol=raw_symbol,
        source_event_ts_ns=source_event_ts_ns,
        instrument=instrument,
        metadata=metadata,
    )
