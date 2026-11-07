"""Fail-closed validation of intraday OHLCV bar intervals against CME sessions.

This is a pure validation boundary. The caller must resolve the provider mapping
to a CanonicalInstrument through the durable registry and supply an explicitly
versioned SessionCalendarRegistry. No symbol parsing or calendar guessing occurs.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from app.instrument_identity import CanonicalInstrument
from app.ohlcv import BUCKET_POLICY_UTC_FIXED_V1, FIXED_INTERVAL_SECONDS, OhlcvBar
from app.session_calendar import (
    SessionCalendarRegistry,
    SessionState,
    datetime_to_epoch_ns,
    lookup_instant,
)


class SessionBarRejected(ValueError):
    """An OHLCV bar cannot be accepted under the selected CME session release."""

    def __init__(self, reason: str, detail: str = "") -> None:
        super().__init__(f"{reason}: {detail}" if detail else reason)
        self.reason = reason


@dataclass(frozen=True, slots=True)
class SessionBarValidation:
    calendar_id: str
    calendar_version: str
    trading_date: str
    session_state: SessionState
    interval_start_ns: int
    interval_end_ns: int


def _epoch_ns_to_utc(timestamp_ns: int) -> datetime:
    seconds, remainder_ns = divmod(timestamp_ns, 1_000_000_000)
    if remainder_ns % 1_000:
        raise SessionBarRejected(
            "unsupported_timestamp_precision",
            "Python calendar lookup requires microsecond-aligned bar timestamps.",
        )
    try:
        return datetime.fromtimestamp(seconds, tz=timezone.utc).replace(
            microsecond=remainder_ns // 1_000
        )
    except (OverflowError, OSError, ValueError) as exc:
        raise SessionBarRejected("malformed_timestamp") from exc


def validate_intraday_bar_session(
    bar: OhlcvBar,
    instrument: CanonicalInstrument,
    calendar_registry: SessionCalendarRegistry,
    *,
    calendar_version: str,
) -> SessionBarValidation:
    """Validate the complete [bar start, bar end) interval against a pinned session.

    The canonical instrument's explicit session_calendar_id selects the
    calendar. The caller must obtain that canonical object from the point-in-time
    provider mapping, not from raw_symbol. Only UTC_FIXED_V1 intraday bars are
    accepted here; session-aligned daily/higher bars have a separate contract.
    """
    if not isinstance(bar, OhlcvBar):
        raise SessionBarRejected("invalid_bar", "Expected an OhlcvBar.")
    if not isinstance(instrument, CanonicalInstrument):
        raise SessionBarRejected("invalid_instrument", "Expected CanonicalInstrument.")
    if not instrument.is_active:
        raise SessionBarRejected("inactive_instrument")
    if instrument.asset_class != "future" or instrument.instrument_type != "future":
        raise SessionBarRejected("unsupported_instrument")
    if not isinstance(calendar_version, str) or not calendar_version.strip():
        raise SessionBarRejected("calendar_version_required")
    if not isinstance(calendar_registry, SessionCalendarRegistry):
        raise SessionBarRejected("calendar_registry_required")
    if bar.bucket_policy != BUCKET_POLICY_UTC_FIXED_V1:
        raise SessionBarRejected(
            "unsupported_bucket_policy",
            "This validator accepts only UTC_FIXED_V1 intraday source bars.",
        )
    interval_seconds = FIXED_INTERVAL_SECONDS.get(bar.timeframe)
    if interval_seconds is None or bar.timeframe == "1d":
        raise SessionBarRejected("unsupported_timeframe", bar.timeframe)

    calendar = calendar_registry.for_instrument(
        instrument, version=calendar_version
    )
    if calendar is None:
        raise SessionBarRejected(
            "calendar_unavailable",
            "No exact calendar release matches canonical instrument metadata and version.",
        )
    if calendar.calendar_id != instrument.session_calendar_id:
        raise SessionBarRejected("calendar_identity_mismatch")

    start = _epoch_ns_to_utc(bar.ts_start_ns)
    lookup = lookup_instant(calendar, start)
    if lookup.state == "unknown":
        raise SessionBarRejected("unknown_calendar_coverage")
    if lookup.state not in {"open", "special-session"}:
        raise SessionBarRejected("outside_trading_session", lookup.state)
    if lookup.session_close_ns is None or lookup.trading_date is None:
        raise SessionBarRejected("invalid_calendar_resolution")

    interval_end_ns = bar.ts_start_ns + interval_seconds * 1_000_000_000
    if interval_end_ns > lookup.session_close_ns:
        raise SessionBarRejected(
            "bar_crosses_session_close",
            "The complete bar interval extends beyond the explicit session close.",
        )

    return SessionBarValidation(
        calendar_id=calendar.calendar_id,
        calendar_version=calendar.version,
        trading_date=lookup.trading_date.isoformat(),
        session_state=lookup.state,
        interval_start_ns=bar.ts_start_ns,
        interval_end_ns=interval_end_ns,
    )
