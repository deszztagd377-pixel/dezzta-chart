import json
import sqlite3

import pytest

from app.instrument_identity import CanonicalInstrument
from app.instrument_registry import (
    InstrumentRelationshipConflict,
    SQLiteInstrumentRegistry,
)

UNDERLYING_ID = "0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a11"
OPTION_ID = "0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a12"
MISSING_ID = "0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a13"


def underlying():
    return CanonicalInstrument(
        canonical_id=UNDERLYING_ID,
        asset_class="equity",
        instrument_type="stock",
        symbol="AAPL",
        venue="XNAS",
        quote_currency="USD",
    )


def option(*, canonical_id=OPTION_ID, underlying_id=UNDERLYING_ID):
    return CanonicalInstrument(
        canonical_id=canonical_id,
        asset_class="option",
        instrument_type="option",
        symbol="AAPL_20261218_C_100",
        venue="XNAS",
        expiration_date="2026-12-18",
        option_right="call",
        strike_price="100",
        settlement_currency="USD",
        contract_multiplier="100",
        underlying_canonical_id=underlying_id,
    )


def downgrade_v3_to_v2(path):
    connection = sqlite3.connect(path)
    try:
        connection.execute("DROP INDEX IF EXISTS ux_canonical_instrument_identity_key")
        connection.execute("ALTER TABLE canonical_instruments DROP COLUMN identity_key")
        connection.execute("DROP TRIGGER validate_option_underlying_before_insert")
        connection.execute("DROP TRIGGER validate_instrument_relationship_before_insert")
        connection.execute("DROP TRIGGER record_option_underlying_after_insert")
        connection.execute("DROP TRIGGER instrument_relationships_are_immutable")
        connection.execute("DROP TRIGGER instrument_relationships_no_delete")
        connection.execute("DROP TABLE canonical_instrument_relationships")
        connection.execute("PRAGMA user_version = 2")
        connection.commit()
    finally:
        connection.close()


def test_option_registration_requires_existing_non_option_underlying(tmp_path):
    registry = SQLiteInstrumentRegistry(str(tmp_path / "registry.sqlite3"))

    with pytest.raises(InstrumentRelationshipConflict, match="underlying instrument must already exist"):
        registry.register_instrument(option())

    assert registry.get_instrument(OPTION_ID) is None

    registry.register_instrument(underlying())
    assert registry.register_instrument(option()) is True
    assert registry.get_instrument(OPTION_ID) == option()

    connection = sqlite3.connect(registry.database_path)
    try:
        assert connection.execute(
            """
            SELECT source_canonical_id, relationship_type, target_canonical_id
            FROM canonical_instrument_relationships
            """
        ).fetchall() == [(OPTION_ID, "underlying", UNDERLYING_ID)]
    finally:
        connection.close()



def test_option_cannot_use_another_option_as_its_underlying(tmp_path):
    registry = SQLiteInstrumentRegistry(str(tmp_path / "registry.sqlite3"))
    registry.register_instrument(underlying())
    registry.register_instrument(option())

    nested_option = option(
        canonical_id=MISSING_ID,
        underlying_id=OPTION_ID,
    )
    with pytest.raises(InstrumentRelationshipConflict, match="cannot be another option"):
        registry.register_instrument(nested_option)

    assert registry.get_instrument(MISSING_ID) is None

def test_option_underlying_relationship_is_database_enforced_and_immutable(tmp_path):
    registry = SQLiteInstrumentRegistry(str(tmp_path / "registry.sqlite3"))
    registry.register_instrument(underlying())
    registry.register_instrument(option())

    connection = sqlite3.connect(registry.database_path)
    try:
        with pytest.raises(sqlite3.IntegrityError, match="instrument_relationship_is_immutable"):
            connection.execute(
                """
                UPDATE canonical_instrument_relationships
                SET target_canonical_id = ?
                WHERE source_canonical_id = ?
                """,
                (MISSING_ID, OPTION_ID),
            )
        with pytest.raises(sqlite3.IntegrityError, match="instrument_relationship_is_immutable"):
            connection.execute(
                "DELETE FROM canonical_instrument_relationships WHERE source_canonical_id = ?",
                (OPTION_ID,),
            )
    finally:
        connection.close()


def test_direct_sql_cannot_insert_option_with_missing_underlying(tmp_path):
    registry = SQLiteInstrumentRegistry(str(tmp_path / "registry.sqlite3"))
    payload = json.dumps(option(underlying_id=MISSING_ID).to_dict(), sort_keys=True, separators=(",", ":"))

    connection = sqlite3.connect(registry.database_path)
    try:
        with pytest.raises(sqlite3.IntegrityError, match="invalid_option_underlying"):
            connection.execute(
                """
                INSERT INTO canonical_instruments (
                    canonical_id, asset_class, instrument_type, symbol, venue,
                    is_active, payload_json
                ) VALUES (?, 'option', 'option', ?, 'XNAS', 1, ?)
                """,
                (OPTION_ID, "AAPL_20261218_C_100", payload),
            )
    finally:
        connection.close()



def test_relationship_table_rejects_edges_not_declared_by_canonical_payload(tmp_path):
    registry = SQLiteInstrumentRegistry(str(tmp_path / "registry.sqlite3"))
    registry.register_instrument(underlying())

    connection = sqlite3.connect(registry.database_path)
    try:
        with pytest.raises(sqlite3.IntegrityError, match="invalid_instrument_relationship"):
            connection.execute(
                """
                INSERT INTO canonical_instrument_relationships (
                    source_canonical_id, relationship_type, target_canonical_id
                ) VALUES (?, 'underlying', ?)
                """,
                (UNDERLYING_ID, MISSING_ID),
            )
    finally:
        connection.close()

def test_v2_migration_backfills_existing_option_relationships(tmp_path):
    path = str(tmp_path / "registry.sqlite3")
    registry = SQLiteInstrumentRegistry(path)
    registry.register_instrument(underlying())
    registry.register_instrument(option())
    downgrade_v3_to_v2(path)

    migrated = SQLiteInstrumentRegistry(path)
    assert migrated.get_instrument(OPTION_ID) == option()

    connection = sqlite3.connect(path)
    try:
        assert connection.execute("PRAGMA user_version").fetchone()[0] == 4
        assert connection.execute(
            """
            SELECT source_canonical_id, relationship_type, target_canonical_id
            FROM canonical_instrument_relationships
            """
        ).fetchall() == [(OPTION_ID, "underlying", UNDERLYING_ID)]
    finally:
        connection.close()


def test_v2_migration_rolls_back_when_legacy_option_underlying_is_missing(tmp_path):
    path = str(tmp_path / "registry.sqlite3")
    registry = SQLiteInstrumentRegistry(path)
    registry.register_instrument(underlying())
    registry.register_instrument(option())
    downgrade_v3_to_v2(path)

    connection = sqlite3.connect(path)
    try:
        connection.execute("DROP TRIGGER canonical_instruments_are_immutable")
        payload = option(underlying_id=MISSING_ID).to_dict()
        connection.execute(
            "UPDATE canonical_instruments SET payload_json = ? WHERE canonical_id = ?",
            (json.dumps(payload, sort_keys=True, separators=(",", ":")), OPTION_ID),
        )
        connection.commit()
    finally:
        connection.close()

    with pytest.raises(sqlite3.IntegrityError, match="invalid_instrument_relationship"):
        SQLiteInstrumentRegistry(path)

    connection = sqlite3.connect(path)
    try:
        assert connection.execute("PRAGMA user_version").fetchone()[0] == 2
        assert connection.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' "
            "AND name = 'canonical_instrument_relationships'"
        ).fetchone() is None
    finally:
        connection.close()
