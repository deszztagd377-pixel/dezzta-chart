"""Versioned, fail-closed CME session calendar primitives.

This module deliberately contains no guessed holiday table. Callers must load
an authoritative, versioned schedule whose effective range explicitly covers
the requested trading date. Missing dates are UNKNOWN, never assumed regular.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from typing import Literal, Mapping
from types import MappingProxyType
from zoneinfo import ZoneInfo

CHICAGO = ZoneInfo("America/Chicago")
CALENDAR_BY_FAMILY = {
    "CME_EQUITY_INDEX": frozenset({"ES", "NQ"}),
    "COMEX_GOLD": frozenset({"GC"}),
}
SessionKind = Literal["regular", "special", "early_close", "delayed_open", "closed"]
SessionState = Literal["open", "maintenance", "closed", "unknown", "special-session"]


def calendar_id_for_product_family(product_family: str) -> str | None:
    """Resolve only an explicitly supplied CME product family; never parse symbols."""
    family = product_family.strip().upper()
    matches = [
        calendar_id for calendar_id, families in CALENDAR_BY_FAMILY.items()
        if family in families
    ]
    return matches[0] if len(matches) == 1 else None


class SessionCalendarRegistry:
    """In-memory registry of immutable, explicitly versioned calendar releases.

    This registry does not fetch or manufacture schedules. A release must be
    constructed from a separately verified source before it can be registered.
    """

    def __init__(self, calendars: tuple["SessionCalendar", ...] = ()) -> None:
        self._calendars: dict[tuple[str, str], SessionCalendar] = {}
        self.replace_all(calendars)

    def __len__(self) -> int:
        return len(self._calendars)

    def register(self, calendar: "SessionCalendar") -> None:
        key = (calendar.calendar_id, calendar.version)
        existing = self._calendars.get(key)
        if existing is not None and existing != calendar:
            raise InvalidSessionCalendar(
                "A calendar release key cannot be replaced with different content."
            )
        self._calendars[key] = calendar

    def replace_all(self, calendars: tuple["SessionCalendar", ...]) -> None:
        staged: dict[tuple[str, str], SessionCalendar] = {}
        for calendar in calendars:
            key = (calendar.calendar_id, calendar.version)
            existing = staged.get(key)
            if existing is not None and existing != calendar:
                raise InvalidSessionCalendar(
                    "Duplicate calendar release key has conflicting content."
                )
            staged[key] = calendar
        self._calendars = staged

    def get(
        self, calendar_id: str, version: str | None = None
    ) -> "SessionCalendar | None":
        if version is not None:
            return self._calendars.get((calendar_id, version))
        candidates = [
            calendar for (stored_id, _), calendar in self._calendars.items()
            if stored_id == calendar_id
        ]
        # Never guess which release is current when multiple versions exist.
        return candidates[0] if len(candidates) == 1 else None

    def for_product_family(
        self, product_family: str, version: str | None = None
    ) -> "SessionCalendar | None":
        calendar_id = calendar_id_for_product_family(product_family)
        if calendar_id is None:
            return None
        calendar = self.get(calendar_id, version)
        if calendar is None or calendar.product_family != product_family.strip().upper():
            return None
        return calendar


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
        if self.kind not in {"regular", "special", "early_close", "delayed_open", "closed"}:
            raise InvalidSessionCalendar("Unsupported session record kind.")
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
        copied_records = dict(self.records)
        for trading_date, record in copied_records.items():
            if trading_date != record.trading_date:
                raise InvalidSessionCalendar("Record key must equal its trading date.")
            if not self.effective_start <= trading_date <= self.effective_end:
                raise InvalidSessionCalendar("Record is outside the declared effective range.")
        object.__setattr__(self, "records", MappingProxyType(copied_records))


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
    for trading_date in candidates:
        record = resolve_trading_date(calendar, trading_date)
        if record is None or record.kind == "closed":
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

    # Classify non-session time only when the schedule explicitly covers
    # the relevant trading date(s). A neighboring record cannot fill a gap.
    wall_time = local.timetz().replace(tzinfo=None)
    if time(16, 0) <= wall_time < time(17, 0):
        current = resolve_trading_date(calendar, local.date())
        following = resolve_trading_date(calendar, local.date() + timedelta(days=1))
        if current is None or following is None:
            return SessionLookup("unknown", calendar_id=calendar.calendar_id,
                                 calendar_version=calendar.version)
        is_regular_maintenance = (
            current.kind == "regular" and following.kind == "regular"
            and current.close_local is not None and following.open_local is not None
            and current.close_local.timetz().replace(tzinfo=None) == time(16, 0)
            and following.open_local.timetz().replace(tzinfo=None) == time(17, 0)
        )
        return SessionLookup(
            "maintenance" if is_regular_maintenance else "closed",
            local.date(), calendar_id=calendar.calendar_id,
            calendar_version=calendar.version,
        )

    target_date = local.date() + timedelta(days=1) if wall_time >= time(17, 0) else local.date()
    target = resolve_trading_date(calendar, target_date)
    if target is None:
        return SessionLookup("unknown", calendar_id=calendar.calendar_id,
                             calendar_version=calendar.version)
    return SessionLookup("closed", target_date,
                         calendar_id=calendar.calendar_id,
                         calendar_version=calendar.version)


@dataclass(frozen=True, slots=True)
class SessionBucket:
    """Session-aligned bucket bounds and the exact calendar release used."""

    timeframe: Literal["1d", "1w", "1M", "3M"]
    trading_period_start: date
    trading_period_end: date
    start_ns: int
    end_ns: int
    calendar_id: str
    calendar_version: str


def session_bucket_bounds(
    calendar: SessionCalendar, trading_date: date, timeframe: str
) -> SessionBucket | None:
    """Resolve exchange-session bucket bounds; None means incomplete schedule.

    Weekly buckets use Monday-Sunday trading-date weeks; monthly and quarterly
    buckets use calendar months. Every date in the period must be explicitly
    represented, including closed dates, before bounds are returned.
    """
    if timeframe not in {"1d", "1w", "1M", "3M"}:
        raise ValueError("Session buckets support only 1d, 1w, 1M, and 3M.")
    if timeframe == "1d":
        start_date = end_date = trading_date
    elif timeframe == "1w":
        start_date = trading_date - timedelta(days=trading_date.weekday())
        end_date = start_date + timedelta(days=6)
    else:
        month_step = 1 if timeframe == "1M" else 3
        start_month = ((trading_date.month - 1) // month_step) * month_step + 1
        start_date = date(trading_date.year, start_month, 1)
        next_month_index = start_month - 1 + month_step
        next_month = date(
            trading_date.year + next_month_index // 12,
            next_month_index % 12 + 1,
            1,
        )
        end_date = next_month - timedelta(days=1)

    if start_date < calendar.effective_start or end_date > calendar.effective_end:
        return None
    days = (end_date - start_date).days + 1
    period_records = [
        resolve_trading_date(calendar, start_date + timedelta(days=offset))
        for offset in range(days)
    ]
    if any(record is None for record in period_records):
        return None
    sessions = [
        record for record in period_records
        if record is not None and record.kind != "closed"
    ]
    if not sessions:
        return None
    first = min(sessions, key=lambda item: item.open_local.astimezone(timezone.utc))
    last = max(sessions, key=lambda item: item.close_local.astimezone(timezone.utc))
    return SessionBucket(
        timeframe=timeframe, trading_period_start=start_date,
        trading_period_end=end_date,
        start_ns=datetime_to_epoch_ns(first.open_local),
        end_ns=datetime_to_epoch_ns(last.close_local),
        calendar_id=calendar.calendar_id,
        calendar_version=calendar.version,
    )
