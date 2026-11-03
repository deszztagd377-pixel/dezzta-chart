"""Account-wide price-alert zone policy.

This module is a pure domain guard. Persistence must re-check the same quota
inside the database transaction that inserts a zone; this function alone does
not protect against concurrent requests.
"""
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Iterable


MAX_ZONES_PER_ACCOUNT = 5


class AlertZoneValidationError(ValueError):
    """The requested price zone is invalid."""


class AlertZoneQuotaExceeded(ValueError):
    """The account already owns the maximum number of saved zones."""


@dataclass(frozen=True, slots=True)
class PriceAlertZone:
    owner_id: str
    canonical_instrument_id: str
    lower_price: Decimal
    upper_price: Decimal
    status: str = "active"
    deleted: bool = False


def _as_finite_decimal(value: Decimal | str | int | float, field: str) -> Decimal:
    try:
        parsed = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise AlertZoneValidationError(f"{field} must be a valid decimal price.") from exc
    if not parsed.is_finite():
        raise AlertZoneValidationError(f"{field} must be finite.")
    return parsed


def validate_zone_creation(
    *,
    owner_id: str,
    canonical_instrument_id: str,
    lower_price: Decimal | str | int | float,
    upper_price: Decimal | str | int | float,
    existing_zones: Iterable[PriceAlertZone],
) -> PriceAlertZone:
    """Validate one new zone and enforce five saved zones across all pairs.

    Paused, triggered, and delivery-failed zones still consume a slot.
    Explicitly deleted zones and zones belonging to another account do not.
    The caller must repeat this quota check atomically in durable storage.
    """
    if not owner_id or not owner_id.strip():
        raise AlertZoneValidationError("owner_id is required.")
    if not canonical_instrument_id or not canonical_instrument_id.strip():
        raise AlertZoneValidationError("canonical_instrument_id is required.")

    lower = _as_finite_decimal(lower_price, "lower_price")
    upper = _as_finite_decimal(upper_price, "upper_price")
    if lower >= upper:
        raise AlertZoneValidationError("lower_price must be less than upper_price.")

    saved_count = sum(
        1
        for zone in existing_zones
        if zone.owner_id == owner_id and not zone.deleted
    )
    if saved_count >= MAX_ZONES_PER_ACCOUNT:
        raise AlertZoneQuotaExceeded(
            f"An account can have at most {MAX_ZONES_PER_ACCOUNT} saved alert zones across all instruments."
        )

    return PriceAlertZone(
        owner_id=owner_id,
        canonical_instrument_id=canonical_instrument_id,
        lower_price=lower,
        upper_price=upper,
    )
