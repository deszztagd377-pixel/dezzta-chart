from decimal import Decimal

import pytest

from app.alerts import (
    AlertZoneQuotaExceeded,
    AlertZoneValidationError,
    PriceAlertZone,
    validate_zone_creation,
)


def _zone(owner: str, instrument: str, status: str = "active", deleted: bool = False):
    return PriceAlertZone(
        owner_id=owner,
        canonical_instrument_id=instrument,
        lower_price=Decimal("100"),
        upper_price=Decimal("110"),
        status=status,
        deleted=deleted,
    )


def test_quota_is_shared_across_all_pairs_for_one_account():
    existing = [
        _zone("account-a", "xauusd", "active"),
        _zone("account-a", "xauusd", "paused"),
        _zone("account-a", "btcusd", "triggered"),
        _zone("account-a", "btcusd", "delivery_failed"),
    ]

    created = validate_zone_creation(
        owner_id="account-a",
        canonical_instrument_id="ethusd",
        lower_price="2000",
        upper_price="2100",
        existing_zones=existing,
    )

    assert created.canonical_instrument_id == "ethusd"
    assert created.lower_price == Decimal("2000")
    assert created.upper_price == Decimal("2100")


def test_sixth_zone_is_rejected_even_when_it_is_for_another_pair():
    existing = [
        _zone("account-a", "xauusd"),
        _zone("account-a", "xauusd"),
        _zone("account-a", "btcusd"),
        _zone("account-a", "btcusd"),
        _zone("account-a", "ethusd"),
    ]

    with pytest.raises(AlertZoneQuotaExceeded):
        validate_zone_creation(
            owner_id="account-a",
            canonical_instrument_id="solusd",
            lower_price="10",
            upper_price="12",
            existing_zones=existing,
        )


def test_other_accounts_and_deleted_zones_do_not_consume_quota():
    existing = [
        _zone("account-b", "xauusd"),
        _zone("account-a", "btcusd", deleted=True),
        *[_zone("account-a", f"pair-{index}") for index in range(4)],
    ]

    created = validate_zone_creation(
        owner_id="account-a",
        canonical_instrument_id="xauusd",
        lower_price="3000",
        upper_price="3010",
        existing_zones=existing,
    )
    assert created.owner_id == "account-a"


@pytest.mark.parametrize(
    ("lower", "upper"),
    [("10", "10"), ("11", "10"), ("NaN", "12"), ("10", "Infinity"), ("bad", "12")],
)
def test_invalid_or_non_finite_zone_prices_are_rejected(lower, upper):
    with pytest.raises(AlertZoneValidationError):
        validate_zone_creation(
            owner_id="account-a",
            canonical_instrument_id="xauusd",
            lower_price=lower,
            upper_price=upper,
            existing_zones=[],
        )


def test_missing_owner_or_canonical_instrument_is_rejected():
    with pytest.raises(AlertZoneValidationError):
        validate_zone_creation(
            owner_id=" ",
            canonical_instrument_id="xauusd",
            lower_price="10",
            upper_price="12",
            existing_zones=[],
        )
