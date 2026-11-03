import sqlite3

import pytest

from app.instrument_identity import CanonicalInstrument
from app.instrument_registry import SQLiteInstrumentRegistry
from app.entitlements import (
    EntitlementUnknownInstrument,
    EntitlementValidationError,
    SQLiteInstrumentEntitlementStore,
)

INSTRUMENT_A = "0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a11"
INSTRUMENT_B = "0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a12"


def _stock(canonical_id: str, symbol: str) -> CanonicalInstrument:
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
def stores(tmp_path):
    path = str(tmp_path / "data" / "registry.sqlite3")
    registry = SQLiteInstrumentRegistry(path)
    registry.register_instrument(_stock(INSTRUMENT_A, "AAPL"))
    registry.register_instrument(_stock(INSTRUMENT_B, "MSFT"))
    return path, SQLiteInstrumentEntitlementStore(path)


def test_entitlements_default_deny_for_unknown_account_and_instrument(stores):
    _, entitlements = stores
    assert entitlements.has_access(subject="firebase-user-a", canonical_instrument_id=INSTRUMENT_A) is False
    assert entitlements.list_for_subject(subject="firebase-user-a") == []


def test_grant_is_scoped_to_account_and_canonical_instrument(stores):
    _, entitlements = stores
    grant = entitlements.grant(subject="firebase-user-a", canonical_instrument_id=INSTRUMENT_A)
    assert grant.status == "active"
    assert entitlements.has_access(subject="firebase-user-a", canonical_instrument_id=INSTRUMENT_A)
    assert not entitlements.has_access(subject="firebase-user-b", canonical_instrument_id=INSTRUMENT_A)
    assert not entitlements.has_access(subject="firebase-user-a", canonical_instrument_id=INSTRUMENT_B)


def test_revoke_immediately_removes_access_and_is_idempotent(stores):
    _, entitlements = stores
    entitlements.grant(subject="firebase-user-a", canonical_instrument_id=INSTRUMENT_A)
    assert entitlements.revoke(subject="firebase-user-a", canonical_instrument_id=INSTRUMENT_A)
    assert not entitlements.has_access(subject="firebase-user-a", canonical_instrument_id=INSTRUMENT_A)
    assert not entitlements.revoke(subject="firebase-user-a", canonical_instrument_id=INSTRUMENT_A)


def test_regrant_restores_one_existing_entitlement_record(stores):
    path, entitlements = stores
    entitlements.grant(subject="firebase-user-a", canonical_instrument_id=INSTRUMENT_A)
    entitlements.revoke(subject="firebase-user-a", canonical_instrument_id=INSTRUMENT_A)
    entitlements.grant(subject="firebase-user-a", canonical_instrument_id=INSTRUMENT_A)
    connection = sqlite3.connect(path)
    try:
        assert connection.execute(
            "SELECT COUNT(*) FROM user_instrument_entitlements"
        ).fetchone()[0] == 1
    finally:
        connection.close()
    assert entitlements.has_access(subject="firebase-user-a", canonical_instrument_id=INSTRUMENT_A)


def test_unknown_instrument_cannot_be_granted(stores):
    _, entitlements = stores
    with pytest.raises(EntitlementUnknownInstrument):
        entitlements.grant(
            subject="firebase-user-a",
            canonical_instrument_id="0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a99",
        )


def test_invalid_subject_and_canonical_id_are_rejected(stores):
    _, entitlements = stores
    with pytest.raises(EntitlementValidationError):
        entitlements.grant(subject=" ", canonical_instrument_id=INSTRUMENT_A)
    with pytest.raises(EntitlementValidationError):
        entitlements.has_access(subject="firebase-user-a", canonical_instrument_id="AAPL")


def test_revoked_entitlements_are_hidden_unless_requested(stores):
    _, entitlements = stores
    entitlements.grant(subject="firebase-user-a", canonical_instrument_id=INSTRUMENT_A)
    entitlements.revoke(subject="firebase-user-a", canonical_instrument_id=INSTRUMENT_A)
    assert entitlements.list_for_subject(subject="firebase-user-a") == []
    revoked = entitlements.list_for_subject(subject="firebase-user-a", include_revoked=True)
    assert len(revoked) == 1 and revoked[0].status == "revoked"


def test_entitlements_survive_store_reopen(stores):
    path, entitlements = stores
    entitlements.grant(subject="firebase-user-a", canonical_instrument_id=INSTRUMENT_A)
    reopened = SQLiteInstrumentEntitlementStore(path)
    assert reopened.has_access(subject="firebase-user-a", canonical_instrument_id=INSTRUMENT_A)


def test_database_foreign_key_rejects_direct_unknown_instrument_grant(stores):
    path, _ = stores
    connection = sqlite3.connect(path)
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                """
                INSERT INTO user_instrument_entitlements (
                    subject, canonical_instrument_id, status, revoked_at_utc
                ) VALUES ('firebase-user-a', ?, 'active', NULL)
                """,
                ("0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a99",),
            )
    finally:
        connection.close()
