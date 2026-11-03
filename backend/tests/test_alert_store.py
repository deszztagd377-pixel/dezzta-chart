from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
import sqlite3

import pytest

from app.alert_store import (
    AlertZoneUnknownInstrument,
    SQLitePriceAlertStore,
)
from app.alerts import AlertZoneQuotaExceeded
from app.instrument_identity import CanonicalInstrument
from app.instrument_registry import SQLiteInstrumentRegistry

INSTRUMENTS = [
    "0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a11",
    "0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a12",
    "0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a13",
    "0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a14",
    "0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a15",
    "0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a16",
]


def _instrument(canonical_id: str, symbol: str) -> CanonicalInstrument:
    return CanonicalInstrument(
        canonical_id=canonical_id,
        asset_class="equity",
        instrument_type="stock",
        symbol=symbol,
        venue="XNAS",
        quote_currency="USD",
        tick_size="0.01",
    )


@pytest.fixture
def store(tmp_path):
    path = str(tmp_path / "data" / "registry.sqlite3")
    registry = SQLiteInstrumentRegistry(path)
    for index, canonical_id in enumerate(INSTRUMENTS):
        registry.register_instrument(_instrument(canonical_id, f"TEST{index}"))
    return SQLitePriceAlertStore(path)


def _create(store, owner="account-a", index=0):
    return store.create_zone(
        owner_id=owner,
        canonical_instrument_id=INSTRUMENTS[index],
        lower_price="100.00",
        upper_price="110.00",
    )


def test_zones_are_durable_and_shared_across_pairs(store):
    _create(store, index=0)
    _create(store, index=1)
    _create(store, index=2)
    reopened = SQLitePriceAlertStore(store.database_path)

    zones = reopened.list_zones(owner_id="account-a")
    assert len(zones) == 3
    assert {zone.canonical_instrument_id for zone in zones} == set(INSTRUMENTS[:3])
    assert zones[0].lower_price == Decimal("100.00")
    assert zones[0].upper_price == Decimal("110.00")


def test_sixth_zone_is_rejected_across_all_instruments(store):
    for index in range(5):
        _create(store, index=index)

    with pytest.raises(AlertZoneQuotaExceeded):
        _create(store, index=5)

    assert len(store.list_zones(owner_id="account-a")) == 5


def test_quota_is_per_account_not_global(store):
    for index in range(5):
        _create(store, owner="account-a", index=index)
    _create(store, owner="account-b", index=5)

    assert len(store.list_zones(owner_id="account-a")) == 5
    assert len(store.list_zones(owner_id="account-b")) == 1


def test_status_changes_do_not_release_quota_but_explicit_delete_does(store):
    zones = [_create(store, index=index) for index in range(5)]
    for status in ("paused", "triggered", "delivery_failed"):
        assert store.set_status(
            owner_id="account-a", zone_id=zones[0].zone_id, status=status
        )
    with pytest.raises(AlertZoneQuotaExceeded):
        _create(store, index=5)

    assert store.delete_zone(owner_id="account-a", zone_id=zones[0].zone_id)
    replacement = _create(store, index=5)
    assert replacement.status == "active"
    assert len(store.list_zones(owner_id="account-a")) == 5
    assert len(store.list_zones(owner_id="account-a", include_deleted=True)) == 6


def test_owner_scope_is_enforced_for_status_and_delete(store):
    zone = _create(store)
    assert not store.set_status(
        owner_id="different-account", zone_id=zone.zone_id, status="paused"
    )
    assert not store.delete_zone(
        owner_id="different-account", zone_id=zone.zone_id
    )
    assert store.list_zones(owner_id="account-a")[0].status == "active"


def test_unknown_canonical_instrument_is_rejected(store):
    with pytest.raises(AlertZoneUnknownInstrument):
        store.create_zone(
            owner_id="account-a",
            canonical_instrument_id="0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a99",
            lower_price="1",
            upper_price="2",
        )


def test_direct_sql_cannot_bypass_account_quota(store):
    for index in range(5):
        _create(store, index=index)

    connection = sqlite3.connect(store.database_path)
    try:
        with pytest.raises(sqlite3.IntegrityError, match="alert_zone_account_quota_exceeded"):
            connection.execute(
                """
                INSERT INTO price_alert_zones (
                    zone_id, owner_id, canonical_instrument_id,
                    lower_price, upper_price, status
                ) VALUES (
                    '00000000-0000-4000-8000-000000000001',
                    'account-a', ?, '1', '2', 'active'
                )
                """,
                (INSTRUMENTS[5],),
            )
    finally:
        connection.close()


def test_concurrent_creates_never_exceed_five_zones(store):
    def attempt(index):
        try:
            _create(store, index=index)
            return "created"
        except AlertZoneQuotaExceeded:
            return "quota"

    with ThreadPoolExecutor(max_workers=6) as executor:
        outcomes = list(executor.map(attempt, range(6)))

    assert outcomes.count("created") == 5
    assert outcomes.count("quota") == 1
    assert len(store.list_zones(owner_id="account-a")) == 5


@pytest.mark.parametrize(
    ("lower", "upper"),
    [("10", "10"), ("11", "10"), ("NaN", "12"), ("10", "Infinity"), ("bad", "12")],
)
def test_invalid_price_ranges_are_rejected(store, lower, upper):
    with pytest.raises(ValueError):
        store.create_zone(
            owner_id="account-a",
            canonical_instrument_id=INSTRUMENTS[0],
            lower_price=lower,
            upper_price=upper,
        )
