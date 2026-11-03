"""Provider-neutral canonical instrument identity contracts.

Canonical IDs are assigned by the instrument registry and must be persisted.
They are deliberately not derived from ticker symbols or provider IDs.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from uuid import UUID


_ASSET_INSTRUMENT_TYPES = {
    "equity": {"stock"},
    "etf": {"etf"},
    "crypto": {"spot", "perpetual"},
    "future": {"future"},
    "option": {"option"},
    "fx": {"fx_pair"},
    "index": {"index"},
}
_ASSET_CLASSES = frozenset(_ASSET_INSTRUMENT_TYPES)
_INSTRUMENT_TYPES = frozenset(
    instrument_type
    for supported in _ASSET_INSTRUMENT_TYPES.values()
    for instrument_type in supported
)


class InvalidCanonicalInstrument(ValueError):
    """Raised when canonical instrument metadata is incomplete or inconsistent."""


def _required_text(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise InvalidCanonicalInstrument(f"{field_name} is required.")
    return value.strip()


def _optional_currency(value: str | None, field_name: str) -> str | None:
    if value is None:
        return None
    normalized = _required_text(value, field_name).upper()
    if not normalized.isalpha() or not 2 <= len(normalized) <= 12:
        raise InvalidCanonicalInstrument(f"{field_name} must be a valid currency or unit code.")
    return normalized


def _positive_decimal(value: str | None, field_name: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise InvalidCanonicalInstrument(f"{field_name} must be a positive decimal string.")
    try:
        parsed = Decimal(value)
    except (InvalidOperation, ValueError):
        raise InvalidCanonicalInstrument(f"{field_name} must be a positive decimal string.") from None
    if not parsed.is_finite() or parsed <= 0:
        raise InvalidCanonicalInstrument(f"{field_name} must be finite and greater than zero.")
    return format(parsed.normalize(), "f")


@dataclass(frozen=True, slots=True)
class CanonicalInstrument:
    """Stable app-level instrument identity independent of any data provider.

    canonical_id must be assigned once by a registry and persisted. A symbol,
    venue, provider ID, or contract month must never be used as its replacement.
    Provider-specific IDs belong in a separate mapping layer.
    """

    canonical_id: str
    asset_class: str
    instrument_type: str
    symbol: str
    venue: str
    name: str | None = None
    base_currency: str | None = None
    quote_currency: str | None = None
    settlement_currency: str | None = None
    expiration_date: str | None = None
    contract_multiplier: str | None = None
    tick_size: str | None = None
    quantity_increment: str | None = None
    option_right: str | None = None
    strike_price: str | None = None
    underlying_canonical_id: str | None = None
    session_calendar_id: str | None = None
    is_active: bool = True

    def __post_init__(self) -> None:
        try:
            canonical_id = str(UUID(_required_text(self.canonical_id, "canonical_id")))
        except (ValueError, AttributeError):
            raise InvalidCanonicalInstrument("canonical_id must be a valid UUID.") from None
        object.__setattr__(self, "canonical_id", canonical_id)

        asset_class = _required_text(self.asset_class, "asset_class").lower()
        instrument_type = _required_text(self.instrument_type, "instrument_type").lower()
        if asset_class not in _ASSET_CLASSES:
            raise InvalidCanonicalInstrument("Unsupported asset_class.")
        if instrument_type not in _INSTRUMENT_TYPES:
            raise InvalidCanonicalInstrument("Unsupported instrument_type.")
        if instrument_type not in _ASSET_INSTRUMENT_TYPES[asset_class]:
            raise InvalidCanonicalInstrument("instrument_type is incompatible with asset_class.")
        object.__setattr__(self, "asset_class", asset_class)
        object.__setattr__(self, "instrument_type", instrument_type)

        symbol = _required_text(self.symbol, "symbol").upper()
        venue = _required_text(self.venue, "venue").upper()
        if len(symbol) > 64 or len(venue) > 64:
            raise InvalidCanonicalInstrument("symbol and venue must be at most 64 characters.")
        object.__setattr__(self, "symbol", symbol)
        object.__setattr__(self, "venue", venue)

        if self.name is not None:
            object.__setattr__(self, "name", _required_text(self.name, "name"))

        for field_name in ("base_currency", "quote_currency", "settlement_currency"):
            object.__setattr__(
                self, field_name, _optional_currency(getattr(self, field_name), field_name)
            )

        if instrument_type in {"spot", "perpetual", "fx_pair"}:
            if not self.base_currency or not self.quote_currency:
                raise InvalidCanonicalInstrument(
                    "base_currency and quote_currency are required for spot, perpetual, and FX instruments."
                )
            if self.base_currency == self.quote_currency:
                raise InvalidCanonicalInstrument("base_currency and quote_currency must differ.")

        if self.expiration_date is not None:
            try:
                normalized_expiration = date.fromisoformat(self.expiration_date).isoformat()
            except (TypeError, ValueError):
                raise InvalidCanonicalInstrument("expiration_date must be an ISO calendar date.") from None
            object.__setattr__(self, "expiration_date", normalized_expiration)

        if instrument_type in {"future", "option"} and self.expiration_date is None:
            raise InvalidCanonicalInstrument("Dated futures and options require expiration_date.")

        for field_name in ("contract_multiplier", "tick_size", "quantity_increment", "strike_price"):
            object.__setattr__(
                self, field_name, _positive_decimal(getattr(self, field_name), field_name)
            )

        if instrument_type in {"perpetual", "future", "option"}:
            if self.settlement_currency is None or self.contract_multiplier is None:
                raise InvalidCanonicalInstrument(
                    "Perpetuals, futures, and options require authoritative "
                    "settlement_currency and contract_multiplier for stable identity."
                )

        if instrument_type == "option":
            if not isinstance(self.option_right, str) or self.option_right.lower() not in {"call", "put"}:
                raise InvalidCanonicalInstrument("Options require option_right 'call' or 'put'.")
            object.__setattr__(self, "option_right", self.option_right.lower())
            if self.strike_price is None or self.underlying_canonical_id is None:
                raise InvalidCanonicalInstrument(
                    "Options require strike_price and underlying_canonical_id."
                )
            try:
                underlying_id = str(UUID(self.underlying_canonical_id))
            except (ValueError, TypeError, AttributeError):
                raise InvalidCanonicalInstrument("underlying_canonical_id must be a valid UUID.") from None
            if underlying_id == canonical_id:
                raise InvalidCanonicalInstrument("An option cannot reference itself as its underlying.")
            object.__setattr__(self, "underlying_canonical_id", underlying_id)
        elif any(value is not None for value in (
            self.option_right, self.strike_price, self.underlying_canonical_id
        )):
            raise InvalidCanonicalInstrument("Option-only fields are valid only for options.")

        if self.session_calendar_id is not None:
            object.__setattr__(
                self, "session_calendar_id",
                _required_text(self.session_calendar_id, "session_calendar_id"),
            )
        if not isinstance(self.is_active, bool):
            raise InvalidCanonicalInstrument("is_active must be a boolean.")

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-compatible mapping; decimal values remain exact strings."""
        return asdict(self)
