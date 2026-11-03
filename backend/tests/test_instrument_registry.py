from concurrent.futures import ThreadPoolExecutor
import json
import sqlite3

import pytest

from app.instrument_identity import CanonicalInstrument
from app.instrument_registry import (
    CanonicalIdentityConflict,
    InstrumentMappingConflict,
    InstrumentRegistryConflict,
    ProviderInstrumentMapping,
    SQLiteInstrumentRegistry,
    UnknownCanonicalInstrument,
    UnsupportedRegistrySchema,
)

INSTRUMENT_ID = "0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a11"
SECOND_ID = "0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a12"


def stock(**overrides):
    values = {
        "canonical_id": INSTRUMENT_ID,
        "asset_class": "equity",
        "instrument_type": "stock",
        "symbol": "AAPL",
        "venue": "XNAS",
        "quote_currency": "USD",
        "tick_size": "0.01",
    }
    values.update(overrides)
    return CanonicalInstrument(**values)


def mapping(**overrides):
    values = {
        "provider": "Databento",
        "dataset": "EQUS.MINI",
        "publisher_id": 1,
        "instrument_id": 9001,
        "raw_symbol": "AAPL",
        "valid_from_ns": 100,
        "valid_to_ns": 200,
        "canonical_id": INSTRUMENT_ID,
        "series_type": "instrument",
    }
    values.update(overrides)
    return ProviderInstrumentMapping(**values)


@pytest.fixture
def registry(tmp_path):
    return SQLiteInstrumentRegistry(str(tmp_path / "data" / "registry.sqlite3"))


def _downgrade_registry_file_to_v1(path):
    """Build a populated v1 fixture without duplicating the production DDL."""
    connection = sqlite3.connect(path)
    try:
        connection.execute("DROP INDEX IF EXISTS ux_canonical_instrument_identity_key")
        connection.execute("ALTER TABLE canonical_instruments DROP COLUMN identity_key")
        connection.execute("DROP TABLE instrument_metadata_revisions")
        # A true v1 fixture predates the v2 metadata table and v3
        # relationship table/triggers; remove later-schema artifacts too.
        for trigger in (
            "validate_option_underlying_before_insert",
            "validate_instrument_relationship_before_insert",
            "record_option_underlying_after_insert",
            "instrument_relationships_are_immutable",
            "instrument_relationships_no_delete",
        ):
            connection.execute(f"DROP TRIGGER IF EXISTS {trigger}")
        connection.execute("DROP TABLE IF EXISTS canonical_instrument_relationships")
        connection.execute("PRAGMA user_version = 1")
        connection.commit()
    finally:
        connection.close()


def test_v1_migration_preserves_data_and_marks_legacy_metadata_unknown(tmp_path):
    path = str(tmp_path / "registry.sqlite3")
    original = SQLiteInstrumentRegistry(path)
    original.register_instrument(stock())
    original.add_provider_mapping(mapping())
    _downgrade_registry_file_to_v1(path)

    migrated = SQLiteInstrumentRegistry(path)
    assert migrated.get_instrument(INSTRUMENT_ID) == stock()
    assert migrated.list_provider_mappings(INSTRUMENT_ID) == [mapping(provider="databento")]

    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    try:
        assert connection.execute("PRAGMA user_version").fetchone()[0] == 4
        rows = connection.execute(
            "SELECT * FROM instrument_metadata_revisions WHERE canonical_id = ?",
            (INSTRUMENT_ID,),
        ).fetchall()
        assert len(rows) == 1
        row = rows[0]
        assert row["source_kind"] == "legacy_migration"
        assert row["source_name"] == "sqlite_registry_v1"
        assert row["source_event_ts_ns"] is None
        assert row["effective_from_ns"] is None
        assert row["effective_to_ns"] is None
        assert row["validity_status"] == "historical_unknown"
        assert row["payload_schema_version"] == 1
        assert row["metadata_json"] == connection.execute(
            "SELECT payload_json FROM canonical_instruments WHERE canonical_id = ?",
            (INSTRUMENT_ID,),
        ).fetchone()[0]
        assert row["received_at_utc"]
    finally:
        connection.close()

    # Reopening a migrated database must not duplicate the migration baseline.
    SQLiteInstrumentRegistry(path)
    connection = sqlite3.connect(path)
    try:
        assert connection.execute(
            "SELECT COUNT(*) FROM instrument_metadata_revisions WHERE canonical_id = ?",
            (INSTRUMENT_ID,),
        ).fetchone()[0] == 1
    finally:
        connection.close()


def test_v1_migration_rolls_back_schema_changes_on_failure(tmp_path):
    path = str(tmp_path / "registry.sqlite3")
    original = SQLiteInstrumentRegistry(path)
    original.register_instrument(stock())
    _downgrade_registry_file_to_v1(path)

    connection = sqlite3.connect(path)
    try:
        # Force a late DDL collision after the migration has created its table
        # and indexes; the transaction must remove those partial changes.
        connection.execute(
            """
            CREATE TRIGGER prevent_metadata_revision_overlap_insert
            BEFORE INSERT ON canonical_instruments
            BEGIN
                SELECT 1;
            END
            """
        )
        connection.commit()
    finally:
        connection.close()

    with pytest.raises(sqlite3.OperationalError, match="already exists"):
        SQLiteInstrumentRegistry(path)

    connection = sqlite3.connect(path)
    try:
        assert connection.execute("PRAGMA user_version").fetchone()[0] == 1
        table = connection.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' "
            "AND name = 'instrument_metadata_revisions'"
        ).fetchone()
        assert table is None
        assert connection.execute(
            "SELECT COUNT(*) FROM canonical_instruments WHERE canonical_id = ?",
            (INSTRUMENT_ID,),
        ).fetchone()[0] == 1
    finally:
        connection.close()


def test_metadata_revision_intervals_are_half_open_and_append_only(tmp_path):
    path = str(tmp_path / "registry.sqlite3")
    registry = SQLiteInstrumentRegistry(path)
    registry.register_instrument(stock())
    connection = sqlite3.connect(path)
    try:
        insert = """
            INSERT INTO instrument_metadata_revisions (
                canonical_id, source_kind, source_name, source_dataset,
                effective_from_ns, effective_to_ns, validity_status,
                payload_schema_version, metadata_json
            ) VALUES (?, 'provider', 'databento', 'EQUS.MINI', ?, ?, 'known', 1, '{}')
        """
        connection.execute(insert, (INSTRUMENT_ID, 100, 200))
        with pytest.raises(sqlite3.IntegrityError, match="overlapping_metadata_revision"):
            connection.execute(insert, (INSTRUMENT_ID, 150, 250))
        connection.execute(insert, (INSTRUMENT_ID, 200, 300))
        connection.execute(insert, (INSTRUMENT_ID, 300, None))

        open_revision = connection.execute(
            """
            SELECT revision_id FROM instrument_metadata_revisions
            WHERE canonical_id = ? AND effective_from_ns = 300
            """,
            (INSTRUMENT_ID,),
        ).fetchone()[0]
        connection.execute(
            "UPDATE instrument_metadata_revisions SET effective_to_ns = 400 "
            "WHERE revision_id = ?",
            (open_revision,),
        )
        with pytest.raises(sqlite3.IntegrityError, match="metadata_revision_is_append_only"):
            connection.execute(
                "UPDATE instrument_metadata_revisions SET metadata_json = '{\"changed\":true}' "
                "WHERE revision_id = ?",
                (open_revision,),
            )
        with pytest.raises(sqlite3.IntegrityError, match="metadata_revision_is_append_only"):
            connection.execute(
                "DELETE FROM instrument_metadata_revisions WHERE revision_id = ?",
                (open_revision,),
            )
        connection.commit()
    finally:
        connection.close()


def test_file_backed_registry_survives_reopen(tmp_path):
    path = str(tmp_path / "registry.sqlite3")
    first = SQLiteInstrumentRegistry(path)
    assert first.register_instrument(stock()) is True
    second = SQLiteInstrumentRegistry(path)
    assert second.get_instrument(INSTRUMENT_ID) == stock()


def test_registration_is_idempotent_but_never_overwrites_identity(registry):
    assert registry.register_instrument(stock()) is True
    assert registry.register_instrument(stock()) is False
    with pytest.raises(InstrumentRegistryConflict):
        registry.register_instrument(stock(symbol="MSFT"))


def test_venue_scoped_identity_rejects_duplicate_uuid_for_same_instrument(registry):
    assert registry.register_instrument(stock()) is True
    with pytest.raises(CanonicalIdentityConflict, match="venue-scoped identity"):
        registry.register_instrument(stock(canonical_id=SECOND_ID))
    assert registry.get_instrument(SECOND_ID) is None


def test_same_symbol_on_different_venues_has_distinct_canonical_identity(registry):
    assert registry.register_instrument(stock()) is True
    assert registry.register_instrument(stock(canonical_id=SECOND_ID, venue="XNAS2")) is True
    assert registry.get_instrument(SECOND_ID).venue == "XNAS2"


def test_currency_pair_identity_ignores_provider_specific_symbol_format(registry):
    first = CanonicalInstrument(
        canonical_id=INSTRUMENT_ID, asset_class="crypto", instrument_type="spot",
        symbol="BTCUSDT", venue="BINANCE", base_currency="BTC", quote_currency="USDT",
    )
    second = CanonicalInstrument(
        canonical_id=SECOND_ID, asset_class="crypto", instrument_type="spot",
        symbol="BTC/USDT", venue="BINANCE", base_currency="BTC", quote_currency="USDT",
    )
    assert registry.register_instrument(first) is True
    with pytest.raises(CanonicalIdentityConflict):
        registry.register_instrument(second)


def test_currency_pair_identity_is_venue_scoped(registry):
    first = CanonicalInstrument(
        canonical_id=INSTRUMENT_ID, asset_class="crypto", instrument_type="spot",
        symbol="BTCUSDT", venue="BINANCE", base_currency="BTC", quote_currency="USDT",
    )
    second = CanonicalInstrument(
        canonical_id=SECOND_ID, asset_class="crypto", instrument_type="spot",
        symbol="BTCUSDT", venue="COINBASE", base_currency="BTC", quote_currency="USDT",
    )
    assert registry.register_instrument(first) is True
    assert registry.register_instrument(second) is True


def test_dated_futures_use_product_and_expiry_as_identity(registry):
    first = CanonicalInstrument(
        canonical_id=INSTRUMENT_ID, asset_class="future", instrument_type="future",
        symbol="ES", venue="XCME", expiration_date="2026-12-18",
        settlement_currency="USD", contract_multiplier="50",
    )
    next_expiry = CanonicalInstrument(
        canonical_id=SECOND_ID, asset_class="future", instrument_type="future",
        symbol="ES", venue="XCME", expiration_date="2027-03-19",
        settlement_currency="USD", contract_multiplier="50",
    )
    assert registry.register_instrument(first) is True
    assert registry.register_instrument(next_expiry) is True


def test_options_use_underlying_expiry_right_and_strike_as_identity(registry):
    underlying_id = "0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a13"
    registry.register_instrument(stock(canonical_id=underlying_id, symbol="SPY", venue="ARCX"))
    call = CanonicalInstrument(
        canonical_id=INSTRUMENT_ID, asset_class="option", instrument_type="option",
        symbol="SPY261218C00500000", venue="ARCX", expiration_date="2026-12-18",
        option_right="call", strike_price="500", underlying_canonical_id=underlying_id,
        settlement_currency="USD", contract_multiplier="100",
    )
    same_contract_different_vendor_symbol = CanonicalInstrument(
        canonical_id=SECOND_ID, asset_class="option", instrument_type="option",
        symbol="SPY-20261218-C-500", venue="ARCX", expiration_date="2026-12-18",
        option_right="call", strike_price="500.00", underlying_canonical_id=underlying_id,
        settlement_currency="USD", contract_multiplier="100",
    )
    assert registry.register_instrument(call) is True
    with pytest.raises(CanonicalIdentityConflict):
        registry.register_instrument(same_contract_different_vendor_symbol)


def test_concurrent_duplicate_identity_registration_has_one_winner(registry):
    candidates = [
        stock(canonical_id=INSTRUMENT_ID),
        stock(canonical_id=SECOND_ID),
    ]

    def insert(candidate):
        try:
            return registry.register_instrument(candidate)
        except CanonicalIdentityConflict:
            return False

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(insert, candidates))
    assert sum(results) == 1
    assert len(registry.list_instruments(active_only=False)) == 1


def test_direct_sql_cannot_bypass_canonical_identity_uniqueness(registry):
    registry.register_instrument(stock())
    duplicate = stock(canonical_id=SECOND_ID).to_dict()
    payload = json.dumps(
        duplicate, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    )
    connection = sqlite3.connect(registry.database_path)
    try:
        with pytest.raises(sqlite3.IntegrityError, match="canonical_instruments.identity_key"):
            connection.execute(
                """
                INSERT INTO canonical_instruments
                (canonical_id, asset_class, instrument_type, symbol, venue, is_active, payload_json)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    duplicate["canonical_id"], duplicate["asset_class"],
                    duplicate["instrument_type"], duplicate["symbol"],
                    duplicate["venue"], int(duplicate["is_active"]), payload,
                ),
            )
    finally:
        connection.close()


def test_direct_sql_rejects_derivative_without_contract_identity_terms(registry):
    payload = stock(canonical_id=SECOND_ID).to_dict()
    payload.update({
        "asset_class": "future",
        "instrument_type": "future",
        "symbol": "ES",
        "venue": "XCME",
        "expiration_date": "2026-12-18",
        "settlement_currency": None,
        "contract_multiplier": None,
    })
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    connection = sqlite3.connect(registry.database_path)
    try:
        with pytest.raises(sqlite3.IntegrityError, match="incomplete_canonical_identity"):
            connection.execute(
                """
                INSERT INTO canonical_instruments
                (canonical_id, asset_class, instrument_type, symbol, venue, is_active, payload_json)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    SECOND_ID, "future", "future", "ES", "XCME", 1, encoded,
                ),
            )
    finally:
        connection.close()


def test_v3_to_v4_migration_rolls_back_when_legacy_derivative_terms_are_missing(tmp_path):
    path = str(tmp_path / "incomplete-v3.sqlite3")
    registry = SQLiteInstrumentRegistry(path)
    registry.register_instrument(stock())
    payload = stock(canonical_id=SECOND_ID).to_dict()
    payload.update({
        "asset_class": "future",
        "instrument_type": "future",
        "symbol": "ES",
        "venue": "XCME",
        "expiration_date": "2026-12-18",
        "settlement_currency": None,
        "contract_multiplier": None,
    })
    connection = sqlite3.connect(path)
    try:
        connection.execute("DROP INDEX ux_canonical_instrument_identity_key")
        connection.execute("ALTER TABLE canonical_instruments DROP COLUMN identity_key")
        connection.execute("DROP TRIGGER canonical_instruments_are_immutable")
        connection.execute("PRAGMA user_version = 3")
        connection.execute(
            """
            INSERT INTO canonical_instruments
            (canonical_id, asset_class, instrument_type, symbol, venue, is_active, payload_json)
            VALUES (?, 'future', 'future', 'ES', 'XCME', 1, ?)
            """,
            (
                SECOND_ID,
                json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True),
            ),
        )
        connection.commit()
    finally:
        connection.close()

    with pytest.raises(sqlite3.IntegrityError, match="incomplete_canonical_identity"):
        SQLiteInstrumentRegistry(path)

    connection = sqlite3.connect(path)
    try:
        assert connection.execute("PRAGMA user_version").fetchone()[0] == 3
        columns = {
            row[1] for row in connection.execute("PRAGMA table_xinfo(canonical_instruments)")
        }
        assert "identity_key" not in columns
        assert connection.execute(
            "SELECT COUNT(*) FROM canonical_instruments WHERE canonical_id = ?",
            (SECOND_ID,),
        ).fetchone()[0] == 1
    finally:
        connection.close()


def test_v3_to_v4_migration_rolls_back_when_legacy_identities_are_duplicated(tmp_path):
    path = str(tmp_path / "duplicate-v3.sqlite3")
    registry = SQLiteInstrumentRegistry(path)
    registry.register_instrument(stock())
    duplicate = stock(canonical_id=SECOND_ID).to_dict()
    payload = __import__("json").dumps(
        duplicate, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    )
    connection = sqlite3.connect(path)
    try:
        connection.execute("DROP INDEX ux_canonical_instrument_identity_key")
        connection.execute("ALTER TABLE canonical_instruments DROP COLUMN identity_key")
        connection.execute("PRAGMA user_version = 3")
        connection.execute(
            """
            INSERT INTO canonical_instruments
            (canonical_id, asset_class, instrument_type, symbol, venue, is_active, payload_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                duplicate["canonical_id"], duplicate["asset_class"],
                duplicate["instrument_type"], duplicate["symbol"],
                duplicate["venue"], int(duplicate["is_active"]), payload,
            ),
        )
        connection.commit()
    finally:
        connection.close()

    with pytest.raises(sqlite3.IntegrityError, match="UNIQUE constraint failed"):
        SQLiteInstrumentRegistry(path)

    connection = sqlite3.connect(path)
    try:
        assert connection.execute("PRAGMA user_version").fetchone()[0] == 3
        columns = {
            row[1] for row in connection.execute("PRAGMA table_xinfo(canonical_instruments)")
        }
        assert "identity_key" not in columns
        assert connection.execute(
            "SELECT COUNT(*) FROM canonical_instruments WHERE canonical_id IN (?, ?)",
            (INSTRUMENT_ID, SECOND_ID),
        ).fetchone()[0] == 2
    finally:
        connection.close()


def test_instrument_metadata_is_database_immutable(registry):
    registry.register_instrument(stock())
    connection = sqlite3.connect(registry.database_path)
    try:
        with pytest.raises(sqlite3.IntegrityError, match="canonical_instrument_is_immutable"):
            connection.execute(
                "UPDATE canonical_instruments SET symbol = 'MSFT' WHERE canonical_id = ?",
                (INSTRUMENT_ID,),
            )
    finally:
        connection.close()


def test_list_filters_and_pagination_are_bounded(registry):
    registry.register_instrument(stock())
    registry.register_instrument(stock(
        canonical_id=SECOND_ID, symbol="BTCUSD", asset_class="crypto", venue="XCRY",
        instrument_type="spot", base_currency="BTC", quote_currency="USD",
    ))
    assert [item.symbol for item in registry.list_instruments(asset_class="equity")] == ["AAPL"]
    assert [item.symbol for item in registry.list_instruments(venue="XNAS")] == ["AAPL"]
    assert registry.list_instruments(limit=1, offset=1)[0].symbol == "AAPL"
    with pytest.raises(ValueError):
        registry.list_instruments(limit=1001)
    with pytest.raises(ValueError):
        registry.list_instruments(offset=-1)


def test_provider_mapping_requires_existing_canonical_instrument(registry):
    with pytest.raises(UnknownCanonicalInstrument):
        registry.add_provider_mapping(mapping())


def test_provider_mapping_resolves_exact_point_in_time_and_survives_reopen(tmp_path):
    path = str(tmp_path / "registry.sqlite3")
    registry = SQLiteInstrumentRegistry(path)
    registry.register_instrument(stock())
    assert registry.add_provider_mapping(mapping()) is True
    assert registry.add_provider_mapping(mapping()) is False
    reopened = SQLiteInstrumentRegistry(path)
    assert reopened.resolve_provider_mapping(
        provider="databento", dataset="EQUS.MINI", publisher_id=1,
        instrument_id=9001, timestamp_ns=100,
    ).canonical_id == INSTRUMENT_ID
    assert reopened.resolve_provider_mapping(
        provider="databento", dataset="EQUS.MINI", publisher_id=1,
        instrument_id=9001, timestamp_ns=199,
    ) is not None
    assert reopened.resolve_provider_mapping(
        provider="databento", dataset="EQUS.MINI", publisher_id=1,
        instrument_id=9001, timestamp_ns=200,
    ) is None


@pytest.mark.parametrize(
    "candidate",
    [
        mapping(valid_from_ns=150, valid_to_ns=250),
        mapping(valid_from_ns=50, valid_to_ns=150),
        mapping(valid_from_ns=100, valid_to_ns=300),
        mapping(valid_from_ns=150, valid_to_ns=None),
    ],
)
def test_overlapping_provider_validity_windows_are_rejected(registry, candidate):
    registry.register_instrument(stock())
    registry.add_provider_mapping(mapping())
    with pytest.raises(InstrumentMappingConflict):
        registry.add_provider_mapping(candidate)


def test_adjacent_provider_validity_windows_are_allowed(registry):
    registry.register_instrument(stock())
    registry.add_provider_mapping(mapping(valid_to_ns=200))
    assert registry.add_provider_mapping(mapping(
        valid_from_ns=200, valid_to_ns=300, raw_symbol="AAPL2"
    )) is True


def test_same_provider_key_can_be_reused_after_closed_validity_window(registry):
    registry.register_instrument(stock())
    registry.register_instrument(stock(canonical_id=SECOND_ID, symbol="AAPL2"))
    registry.add_provider_mapping(mapping(valid_to_ns=200))
    registry.add_provider_mapping(mapping(
        valid_from_ns=200, valid_to_ns=None,
        canonical_id=SECOND_ID, raw_symbol="AAPL2",
    ))
    assert registry.resolve_provider_mapping(
        provider="databento", dataset="EQUS.MINI", publisher_id=1,
        instrument_id=9001, timestamp_ns=199,
    ).canonical_id == INSTRUMENT_ID
    assert registry.resolve_provider_mapping(
        provider="databento", dataset="EQUS.MINI", publisher_id=1,
        instrument_id=9001, timestamp_ns=200,
    ).canonical_id == SECOND_ID


def test_provider_and_dataset_scope_are_isolated(registry):
    registry.register_instrument(stock())
    registry.add_provider_mapping(mapping())
    assert registry.resolve_provider_mapping(
        provider="other-provider", dataset="EQUS.MINI", publisher_id=1,
        instrument_id=9001, timestamp_ns=150,
    ) is None
    assert registry.resolve_provider_mapping(
        provider="databento", dataset="OTHER.DATASET", publisher_id=1,
        instrument_id=9001, timestamp_ns=150,
    ) is None


def test_sql_trigger_rejects_overlap_even_when_bypassing_repository(registry):
    registry.register_instrument(stock())
    registry.add_provider_mapping(mapping())
    connection = sqlite3.connect(registry.database_path)
    try:
        with pytest.raises(sqlite3.IntegrityError, match="overlapping_provider_mapping"):
            connection.execute(
                """
                INSERT INTO provider_instrument_mappings
                (provider,dataset,publisher_id,instrument_id,raw_symbol,valid_from_ns,
                 valid_to_ns,canonical_id,series_type)
                VALUES ('databento','EQUS.MINI',1,9001,'OTHER',150,250,?,'instrument')
                """,
                (INSTRUMENT_ID,),
            )
    finally:
        connection.close()


def test_concurrent_overlapping_writes_cannot_both_succeed(registry):
    registry.register_instrument(stock())
    candidates = [
        mapping(valid_from_ns=100, valid_to_ns=200),
        mapping(valid_from_ns=150, valid_to_ns=250),
    ]

    def insert(candidate):
        try:
            return registry.add_provider_mapping(candidate)
        except InstrumentMappingConflict:
            return False

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(insert, candidates))
    assert sum(results) == 1
    assert len(registry.list_provider_mappings(INSTRUMENT_ID)) == 1


def test_rejects_memory_database_and_newer_schema(tmp_path):
    with pytest.raises(ValueError, match="file-backed"):
        SQLiteInstrumentRegistry(":memory:")
    path = str(tmp_path / "future.sqlite3")
    connection = sqlite3.connect(path)
    connection.execute("PRAGMA user_version = 999")
    connection.close()
    with pytest.raises(UnsupportedRegistrySchema):
        SQLiteInstrumentRegistry(path)


@pytest.mark.parametrize(
    "overrides",
    [
        {"provider": ""},
        {"publisher_id": 0},
        {"instrument_id": 0},
        {"instrument_id": True},
        {"valid_from_ns": -1},
        {"valid_from_ns": 9_223_372_036_854_775_807},
        {"valid_to_ns": 100},
        {"canonical_id": "not-a-uuid"},
    ],
)
def test_invalid_provider_mapping_metadata_is_rejected(registry, overrides):
    registry.register_instrument(stock())
    with pytest.raises(ValueError):
        registry.add_provider_mapping(mapping(**overrides))


def test_mapping_resolution_rejects_timestamp_outside_sqlite_integer_range(registry):
    registry.register_instrument(stock())
    with pytest.raises(ValueError, match="SQLite-range"):
        registry.resolve_provider_mapping(
            provider="databento", dataset="EQUS.MINI", publisher_id=1,
            instrument_id=9001, timestamp_ns=9_223_372_036_854_775_808,
        )


def test_atomic_registration_creates_identity_and_mapping_and_is_idempotent(registry):
    instrument = stock()
    provider_mapping = mapping()
    assert registry.register_instrument_with_mapping(instrument, provider_mapping) == (True, True)
    assert registry.register_instrument_with_mapping(instrument, provider_mapping) == (False, False)
    assert registry.get_instrument(INSTRUMENT_ID) == instrument
    resolved = registry.list_provider_mappings(INSTRUMENT_ID)
    assert len(resolved) == 1
    assert resolved[0].provider == "databento"
    assert resolved[0].dataset == "EQUS.MINI"
    assert resolved[0].canonical_id == INSTRUMENT_ID


def test_atomic_registration_adds_mapping_to_existing_identity(registry):
    instrument = stock()
    registry.register_instrument(instrument)
    assert registry.register_instrument_with_mapping(instrument, mapping()) == (False, True)


def test_atomic_registration_rolls_back_new_identity_on_mapping_conflict(registry):
    registry.register_instrument(stock())
    registry.add_provider_mapping(mapping())

    second = stock(canonical_id=SECOND_ID, symbol="AAPL2")
    conflicting = mapping(
        valid_from_ns=150, valid_to_ns=250,
        canonical_id=SECOND_ID, raw_symbol="AAPL2",
    )
    with pytest.raises(InstrumentMappingConflict):
        registry.register_instrument_with_mapping(second, conflicting)

    assert registry.get_instrument(SECOND_ID) is None
    resolved = registry.list_provider_mappings(INSTRUMENT_ID)
    assert len(resolved) == 1
    assert resolved[0].canonical_id == INSTRUMENT_ID
    assert resolved[0].valid_from_ns == 100
    assert resolved[0].valid_to_ns == 200


def test_atomic_registration_rejects_mismatched_canonical_ids(registry):
    with pytest.raises(ValueError, match="must match"):
        registry.register_instrument_with_mapping(stock(), mapping(canonical_id=SECOND_ID))
    assert registry.get_instrument(INSTRUMENT_ID) is None
