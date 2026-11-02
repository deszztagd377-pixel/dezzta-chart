"""Pure adapter: Databento OHLCV records -> canonical OhlcvBar.

Records are duck-typed (attribute access) exactly like databento_definitions.
UNKNOWN / UNVERIFIED against a real SDK in this repository: the attribute names
used here (open, high, low, close, volume, instrument_id, publisher_id,
ts_event) and the meaning of ``ts_event`` as the bar OPEN time. A wrong
assumption surfaces as rejected records (counted), never as fabricated data.
No float conversion is ever applied; prices stay exact fixed-point integers
(1 unit = 1e-9) until converted to Decimal here.
"""
from __future__ import annotations

import operator
from decimal import Decimal
from typing import Any

from app.ohlcv import InvalidOhlcvBar, OhlcvBar
from app.symbology import InstrumentResolver

UNDEF_PRICE = 9_223_372_036_854_775_807  # INT64_MAX sentinel for "no price"
UNDEF_TIMESTAMP = 18_446_744_073_709_551_615  # UINT64_MAX sentinel
_SCALE = 1_000_000_000
_MISSING = object()

SCHEMA_TIMEFRAMES: dict[str, str] = {
    "ohlcv-1s": "1s", "ohlcv-1m": "1m", "ohlcv-1h": "1h", "ohlcv-1d": "1d",
}
_REQUIRED = (
    "open", "high", "low", "close", "volume",
    "instrument_id", "publisher_id", "ts_event",
)


class RecordRejected(ValueError):
    """A record was not converted. ``reason`` is a stable counter key."""

    def __init__(self, reason: str, detail: str = "") -> None:
        super().__init__(f"{reason}: {detail}" if detail else reason)
        self.reason = reason


def fixed_point_to_decimal(raw: int) -> Decimal:
    """Exact conversion of a signed 1e-9 fixed-point integer (no floats)."""
    negative = raw < 0
    whole, fraction = divmod(abs(raw), _SCALE)
    text = f"{whole}.{str(fraction).rjust(9, '0').rstrip('0')}".rstrip(".")
    return Decimal(f"-{text}" if negative and (whole or fraction) else text)


def _integer(record: Any, name: str) -> int:
    value = getattr(record, name, _MISSING)
    if value is _MISSING:
        raise RecordRejected("unsupported_record", f"missing {name}")
    if isinstance(value, bool):
        raise RecordRejected("malformed", f"{name} is not an integer")
    try:
        return operator.index(value)  # ints and numpy integers; rejects float/str
    except TypeError as exc:
        raise RecordRejected("malformed", f"{name} is not an integer") from exc


def record_to_bar(
    record: Any,
    *,
    resolver: InstrumentResolver,
    provider: str,
    dataset: str,
    schema: str,
    ts_received_ns: int,
    sequence: int,
) -> OhlcvBar:
    """Convert one OHLCV record. Raises RecordRejected for anything unsafe."""
    timeframe = SCHEMA_TIMEFRAMES.get(schema)
    if timeframe is None:
        raise RecordRejected("unsupported_schema", schema)
    if record is None or any(getattr(record, n, _MISSING) is _MISSING for n in _REQUIRED):
        raise RecordRejected("unsupported_record", "not an OHLCV record")

    prices = {}
    for name in ("open", "high", "low", "close"):
        raw = _integer(record, name)
        if raw == UNDEF_PRICE:
            raise RecordRejected("undefined_price", name)
        prices[name] = fixed_point_to_decimal(raw)
    volume = _integer(record, "volume")
    if volume < 0:
        raise RecordRejected("malformed", "negative volume")
    instrument_id = _integer(record, "instrument_id")
    publisher_id = _integer(record, "publisher_id")
    ts_event = _integer(record, "ts_event")
    if min(instrument_id, publisher_id, ts_event) < 0 or ts_event == UNDEF_TIMESTAMP:
        raise RecordRejected("malformed", "negative or undefined identifier/timestamp")

    mapping = resolver.resolve(provider, dataset, publisher_id, instrument_id, ts_event)
    if mapping is None:
        raise RecordRejected("unknown_instrument", f"id={instrument_id}")
    try:
        return OhlcvBar(
            dataset=dataset, publisher_id=publisher_id, instrument_id=instrument_id,
            raw_symbol=mapping.raw_symbol, timeframe=timeframe,  # type: ignore[arg-type]
            ts_start_ns=ts_event, volume=Decimal(volume),
            ts_event_ns=ts_event, ts_received_ns=ts_received_ns,
            sequence=sequence, sequence_origin="local", provider=provider,
            series_type=mapping.series_type, origin="provider",
            **prices,
        )
    except InvalidOhlcvBar as exc:
        raise RecordRejected("invalid_bar", str(exc)) from exc