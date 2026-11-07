"""Versioned, fail-closed CME session calendar primitives.

This module deliberately contains no guessed holiday table. Callers must load
an authoritative, versioned schedule whose effective range explicitly covers
the requested trading date. Missing dates are UNKNOWN, never assumed regular.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from typing import Literal, Mapping
from zoneinfo import ZoneInfo

CHICAGO = ZoneInfo("America/Chicago")
CALENDAR_BY_FAMILY = {
    "CME_EQUITY_INDEX": frozenset({"ES", "NQ"}),
    "COMEX_GOLD": frozenset({"GC"}),
}
SessionKind = Literal["regular", "special", "early_close", "delayed_open", "closed"]
SessionState = Literal["open", "maintenance", "closed", "unknown", "special-session"]


class InvalidSessionCalendar(ValueError):
    """Calendar metadata or a supplied session record is invalid."""


@dataclass(frozen=True, slots=True)
class SessionRecord:
    """One explicitly sourced CME trading-date record.

    Open and close are Chicago-local, timezone-aware instants. A closed date
    has neither boundary. A missing record is not equivalent to a closure.
    """

    trading_date: date
    kind: SessionKind
    open_local: datetime | None
    close_local: datetime | None

    def __post_init__(self) -> None:
        if self.kind == "closed":
            if self.open_local is not None or self.close_local is not None:
                raise InvalidSessionCalendar("Closed dates must not have session boundaries.")
            return
        if self.open_local is None or self.close_local is None:
            raise InvalidSessionCalendar("Open session records require both boundaries.")
        for boundary in (self.open_local, self.close_local):
            if boundary.tzinfo is None or boundary.utcoffset() is None:
                raise InvalidSessionCalendar("Session boundaries must be timezone-aware.")
            if getattr(boundary.tzinfo, "key", None) != "America/Chicago":
                raise InvalidSessionCalendar("Session boundaries must use America/Chicago.")
        if self.close_local.astimezone(timezone.utc) <= self.open_local.astimezone(timezone.utc):
            raise InvalidSessionCalendar("Session close must be after session open.")


@dataclass(frozen=True, slots=True)
class SessionCalendar:
    """Immutable schedule release with explicit provenance and coverage."""

    calendar_id: str
    version: str
    product_family: str
    effective_start: date
    effective_end: date
    source_id: str
    source_url: str
    published_at_utc: datetime
    checksum: str
    records: Mapping[date, SessionRecord]

    def __post_init__(self) -> None:
        if self.calendar_id not in CALENDAR_BY_FAMILY:
            raise InvalidSessionCalendar("Unsupported CME calendar identifier.")
        if self.product_family not in CALENDAR_BY_FAMILY[self.calendar_id]:
            raise InvalidSessionCalendar("Product family does not match calendar identifier.")
        if not self.version.strip() or not self.source_id.strip() or not self.source_url.startswith("https://"):
            raise InvalidSessionCalendar("Version and HTTPS source provenance are required.")
        if not self.checksum.strip():
            raise InvalidSessionCalendar("An immutable source checksum is required.")
        if self.effective_end < self.effective_start:
            raise InvalidSessionCalendar("Calendar effective range is reversed.")
        if self.published_at_utc.tzinfo is None or self.published_at_utc.utcoffset() is None:
            raise InvalidSessionCalendar("Publication timestamp must be timezone-aware.")
        for trading_date, record in self.records.items():
            if trading_date != record.trading_date:
                raise InvalidSessionCalendar("Record key must equal its trading date.")
            if not self.effective_start <= trading_date <= self.effective_end:
                raise InvalidSessionCalendar("Record is outside the declared effective range.")


def resolve_trading_date(
    calendar: SessionCalendar, trading_date: date
) -> SessionRecord | None:
    """Return an explicit record; None means UNKNOWN, not closed."""
    if not calendar.effective_start <= trading_date <= calendar.effective_end:
        return None
    return calendar.records.get(trading_date)


def datetime_to_epoch_ns(value: datetime) -> int:
    """Convert an aware datetime to integer epoch nanoseconds without floats."""
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("An aware datetime is required.")
    utc_value = value.astimezone(timezone.utc)
    epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
    delta = utc_value - epoch
    return ((delta.days * 86_400 + delta.seconds) * 1_000_000
            + delta.microseconds) * 1_000


@dataclass(frozen=True, slots=True)
class SessionLookup:
    state: SessionState
    trading_date: date | None = None
    session_open_ns: int | None = None
    session_close_ns: int | None = None
    calendar_id: str | None = None
    calendar_version: str | None = None


def lookup_instant(calendar: SessionCalendar, instant: datetime) -> SessionLookup:
    """Classify an instant using only explicit records in the calendar release.

    The local date and adjacent trading dates are inspected so a Sunday 17:00
    reopen can be assigned to Monday's trading date without fixed-UTC offsets.
    No session is synthesized when the calendar lacks a required record.
    """
    if instant.tzinfo is None or instant.utcoffset() is None:
        raise ValueError("An aware instant is required.")
    local = instant.astimezone(CHICAGO)
    candidates = (local.date() - timedelta(days=1), local.date(), local.date() + timedelta(days=1))
    known: list[SessionRecord] = []
    for trading_date in candidates:
        record = resolve_trading_date(calendar, trading_date)
        if record is None:
            continue
        known.append(record)
        if record.kind == "closed":
            continue
        assert record.open_local is not None and record.close_local is not None
        if record.open_local.astimezone(timezone.utc) <= instant.astimezone(timezone.utc) < record.close_local.astimezone(timezone.utc):
            if record.kind == "regular":
                state: SessionState = "open"
            else:
                state = "special-session"
            return SessionLookup(
                state, record.trading_date,
                datetime_to_epoch_ns(record.open_local),
                datetime_to_epoch_ns(record.close_local),
                calendar.calendar_id, calendar.version,
            )

    # A covered schedule with no active session is closed/maintenance;
    # absent schedule coverage remains unknown rather than guessed.
    if not known:
        return SessionLookup("unknown", calendar_id=calendar.calendar_id,
                             calendar_version=calendar.version)
    wall_time = local.timetz().replace(tzinfo=None)
    state = "maintenance" if time(16, 0) <= wall_time < time(17, 0) else "closed"
    nearest = next((r for r in known if r.kind != "closed"), None)
    return SessionLookup(state, nearest.trading_date if nearest else None,
                         calendar_id=calendar.calendar_id,
                         calendar_version=calendar.version)
