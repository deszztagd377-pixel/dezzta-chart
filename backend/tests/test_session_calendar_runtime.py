import hashlib
import json
from datetime import datetime, timezone
from decimal import Decimal

from app.config import Settings
from app.instrument_identity import CanonicalInstrument
from app.instrument_registry import ProviderInstrumentMapping
from app.main import create_app
from app.ohlcv import BUCKET_POLICY_UTC_FIXED_V1, OhlcvBar
from app.session_calendar_runtime import load_session_calendar_runtime


def _calendar_payload():
    return {
        "schema_version": 2,
        "calendar_id": "CME_EQUITY_INDEX",
        "version": "2026.11.1",
        "product_family": "ES",
        "effective_start": "2026-11-02",
        "effective_end": "2026-11-03",
        "timezone": "America/Chicago",
        "source": {
            "source_id": "test-fixture-only",
            "source_url": "https://www.cmegroup.com/markets/equities.html",
            "published_at_utc": "2026-10-20T12:00:00Z",
        },
        "records": [
            {
                "trading_date": "2026-11-02",
                "kind": "regular",
                "open_local": "2026-11-01T17:00:00",
                "close_local": "2026-11-02T16:00:00",
                "segments": [
                    {
                        "start_local": "2026-11-01T17:00:00",
                        "end_local": "2026-11-02T16:00:00",
                    }
                ],
            },
            {
                "trading_date": "2026-11-03",
                "kind": "closed",
                "open_local": None,
                "close_local": None,
            },
        ],
    }


def _artifact_bytes():
    return json.dumps(
        _calendar_payload(), separators=(",", ":"), sort_keys=True
    ).encode("utf-8")


def _settings(tmp_path, *, artifact_path="", digest="", version=""):
    return Settings(
        app_env="test",
        market_data_ws_token="test-secret",
        cors_allowed_origins=("http://localhost:5173",),
        instrument_registry_db_path=str(tmp_path / "registry.sqlite3"),
        session_calendar_artifact_path=artifact_path,
        session_calendar_sha256=digest,
        session_calendar_version=version,
    )


def _future_mapping(application):
    canonical_id = "12345678-1234-5678-1234-567812345678"
    application.state.instrument_registry.register_instrument_with_mapping(
        CanonicalInstrument(
            canonical_id=canonical_id,
            asset_class="future",
            instrument_type="future",
            symbol="ESZ6",
            venue="XCME",
            expiration_date="2026-12-18",
            settlement_currency="USD",
            contract_multiplier="50",
            tick_size="0.25",
            session_calendar_id="CME_EQUITY_INDEX",
        ),
        ProviderInstrumentMapping(
            provider="databento",
            dataset="GLBX.MDP3",
            publisher_id=1,
            instrument_id=101,
            raw_symbol="ESZ6",
            valid_from_ns=1,
            valid_to_ns=None,
            canonical_id=canonical_id,
        ),
    )


def _valid_bar():
    start_ns = int(datetime(
        2026, 11, 2, 15, 0, tzinfo=timezone.utc
    ).timestamp() * 1_000_000_000)
    return OhlcvBar(
        dataset="GLBX.MDP3",
        publisher_id=1,
        instrument_id=101,
        raw_symbol="ESZ6",
        timeframe="1m",
        ts_start_ns=start_ns,
        open=Decimal("5000"),
        high=Decimal("5001"),
        low=Decimal("4999"),
        close=Decimal("5000.5"),
        volume=Decimal("10"),
        ts_event_ns=start_ns,
        ts_received_ns=start_ns + 1_000_000,
        sequence=1,
        provider="databento",
        bucket_policy=BUCKET_POLICY_UTC_FIXED_V1,
    )


def _process_bar(application, monkeypatch, bar):
    import app.ingest as ingest_module

    monkeypatch.setattr(ingest_module, "record_to_bar", lambda *args, **kwargs: bar)
    application.state.ingestion._process(
        object(), "ohlcv-1s", bar.ts_received_ns, 0, live=False
    )



def test_ingestion_derives_and_persists_cme_daily_from_validated_intraday_and_revisions(
    tmp_path, monkeypatch
):
    from dataclasses import replace
    from app.ohlcv import BUCKET_POLICY_CME_SESSION_V1

    path = tmp_path / "calendar.json"
    raw = _artifact_bytes()
    path.write_bytes(raw)
    digest = hashlib.sha256(raw).hexdigest()
    application = create_app(_settings(
        tmp_path,
        artifact_path=str(path),
        digest=digest,
        version="2026.11.1",
    ))
    _future_mapping(application)

    first = _valid_bar()
    second = replace(
        first,
        ts_start_ns=first.ts_start_ns + 60_000_000_000,
        ts_event_ns=first.ts_event_ns + 60_000_000_000,
        ts_received_ns=first.ts_received_ns + 60_000_000_000,
        sequence=2,
        open=Decimal("5000.5"),
        high=Decimal("5002"),
        low=Decimal("5000"),
        close=Decimal("5001.5"),
        volume=Decimal("20"),
    )

    _process_bar(application, monkeypatch, first)
    _process_bar(application, monkeypatch, second)

    daily = application.state.ohlcv_pipeline.list_bars(
        timeframe="1d", bucket_policy=BUCKET_POLICY_CME_SESSION_V1
    )
    assert len(daily) == 1
    assert (daily[0].open, daily[0].high, daily[0].low, daily[0].close) == (
        Decimal("5000"), Decimal("5002"), Decimal("4999"), Decimal("5001.5")
    )
    assert daily[0].volume == Decimal("30")
    assert daily[0].calendar_id == "CME_EQUITY_INDEX"
    assert daily[0].calendar_version == "2026.11.1"
    assert daily[0].completeness == "partial"

    # A corrected first minute must rebuild the same daily identity from the
    # retained child set, not add the corrected volume a second time.
    corrected_first = replace(
        first,
        sequence=3,
        high=Decimal("5003"),
        close=Decimal("5000.75"),
        volume=Decimal("15"),
    )
    _process_bar(application, monkeypatch, corrected_first)

    revised_daily = application.state.ohlcv_pipeline.list_bars(
        timeframe="1d", bucket_policy=BUCKET_POLICY_CME_SESSION_V1
    )
    assert len(revised_daily) == 1
    assert revised_daily[0].high == Decimal("5003")
    assert revised_daily[0].close == Decimal("5001.5")
    assert revised_daily[0].volume == Decimal("35")
    assert revised_daily[0].calendar_id == "CME_EQUITY_INDEX"
    assert revised_daily[0].calendar_version == "2026.11.1"

    persisted = application.state.ohlcv_store.load_bars()
    persisted_daily = [
        item for item in persisted
        if item.timeframe == "1d"
        and item.bucket_policy == BUCKET_POLICY_CME_SESSION_V1
    ]
    assert len(persisted_daily) == 1
    assert persisted_daily[0] == revised_daily[0]

    # The provider's one-minute source series keeps its original UTC identity.
    source = application.state.ohlcv_pipeline.list_bars(
        timeframe="1m", bucket_policy=BUCKET_POLICY_UTC_FIXED_V1
    )
    assert len(source) == 2
    assert all(item.calendar_id == "" and item.calendar_version == "" for item in source)

def test_runtime_without_release_is_explicitly_unconfigured():
    registry, status = load_session_calendar_runtime(
        artifact_path="", expected_sha256="", expected_version=""
    )

    assert len(registry) == 0
    assert status == {"state": "unconfigured", "reason": "release_not_configured"}


def test_runtime_rejects_digest_and_version_mismatch(tmp_path):
    path = tmp_path / "calendar.json"
    path.write_bytes(_artifact_bytes())

    wrong_digest_registry, wrong_digest_status = load_session_calendar_runtime(
        artifact_path=str(path),
        expected_sha256="0" * 64,
        expected_version="2026.11.1",
    )
    assert len(wrong_digest_registry) == 0
    assert wrong_digest_status["state"] == "unavailable"

    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    wrong_version_registry, wrong_version_status = load_session_calendar_runtime(
        artifact_path=str(path),
        expected_sha256=digest,
        expected_version="2026.11.2",
    )
    assert len(wrong_version_registry) == 0
    assert wrong_version_status["state"] == "unavailable"


def test_app_wires_fail_closed_validator_before_persistence_without_calendar(
    tmp_path, monkeypatch
):
    application = create_app(_settings(tmp_path))
    _future_mapping(application)
    bar = _valid_bar()

    assert application.state.session_calendar_status["state"] == "unconfigured"
    assert application.state.ingestion.bar_validator is not None

    _process_bar(application, monkeypatch, bar)

    assert application.state.ingestion.counters["rejected_validation_calendar_version_required"] == 1
    assert application.state.ohlcv_pipeline.list_bars(timeframe="1m") == []
    assert application.state.ohlcv_store.load_bars() == []


def test_app_accepts_future_bar_only_with_matching_pinned_release(
    tmp_path, monkeypatch
):
    path = tmp_path / "calendar.json"
    raw = _artifact_bytes()
    path.write_bytes(raw)
    digest = hashlib.sha256(raw).hexdigest()
    application = create_app(_settings(
        tmp_path,
        artifact_path=str(path),
        digest=digest,
        version="2026.11.1",
    ))
    _future_mapping(application)
    bar = _valid_bar()

    assert application.state.session_calendar_status["state"] == "available"
    _process_bar(application, monkeypatch, bar)

    assert application.state.ingestion.counters["inserted"] == 1
    assert len(application.state.ohlcv_pipeline.list_bars(timeframe="1m")) == 1
    persisted = application.state.ohlcv_store.load_bars()
    assert any(
        item.timeframe == "1m" and item.origin == "provider"
        for item in persisted
    )


def test_app_rejects_bar_when_calendar_artifact_pin_is_invalid(tmp_path, monkeypatch):
    path = tmp_path / "calendar.json"
    path.write_bytes(_artifact_bytes())
    application = create_app(_settings(
        tmp_path,
        artifact_path=str(path),
        digest="0" * 64,
        version="2026.11.1",
    ))
    _future_mapping(application)
    bar = _valid_bar()

    assert application.state.session_calendar_status["state"] == "unavailable"
    _process_bar(application, monkeypatch, bar)

    assert application.state.ingestion.counters["rejected_validation_calendar_unavailable"] == 1
    assert application.state.ohlcv_pipeline.list_bars(timeframe="1m") == []
    assert application.state.ohlcv_store.load_bars() == []


def test_runtime_loads_multiple_pinned_calendar_releases_atomically(tmp_path):
    equity_path = tmp_path / "equity.json"
    gold_path = tmp_path / "gold.json"
    equity_raw = _artifact_bytes()
    gold_payload = _calendar_payload()
    gold_payload["calendar_id"] = "COMEX_GOLD"
    gold_payload["product_family"] = "GC"
    gold_payload["version"] = "2026.11.gc1"
    gold_raw = json.dumps(gold_payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    equity_path.write_bytes(equity_raw)
    gold_path.write_bytes(gold_raw)
    registry, status = load_session_calendar_runtime(
        artifact_path="", expected_sha256="", expected_version="",
        releases=((str(equity_path), hashlib.sha256(equity_raw).hexdigest(), "2026.11.1"),
                  (str(gold_path), hashlib.sha256(gold_raw).hexdigest(), "2026.11.gc1")),
    )
    assert len(registry) == 2
    assert registry.get("CME_EQUITY_INDEX", "2026.11.1") is not None
    assert registry.get("COMEX_GOLD", "2026.11.gc1") is not None
    assert status["state"] == "available"
    assert status["release_count"] == 2


def test_runtime_multi_release_manifest_fails_closed_on_one_bad_pin(tmp_path):
    equity_path = tmp_path / "equity.json"
    gold_path = tmp_path / "gold.json"
    equity_raw = _artifact_bytes()
    gold_payload = _calendar_payload()
    gold_payload["calendar_id"] = "COMEX_GOLD"
    gold_payload["product_family"] = "GC"
    gold_raw = json.dumps(gold_payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    equity_path.write_bytes(equity_raw)
    gold_path.write_bytes(gold_raw)
    registry, status = load_session_calendar_runtime(
        artifact_path="", expected_sha256="", expected_version="",
        releases=((str(equity_path), hashlib.sha256(equity_raw).hexdigest(), "2026.11.1"),
                  (str(gold_path), "0" * 64, "2026.11.1")),
    )
    assert len(registry) == 0
    assert status == {"state": "unavailable", "reason": "release_validation_failed"}


def test_runtime_rejects_multiple_versions_for_one_calendar_id(tmp_path):
    first_path = tmp_path / "equity-v1.json"
    second_path = tmp_path / "equity-v2.json"
    first_raw = _artifact_bytes()
    second_payload = _calendar_payload()
    second_payload["version"] = "2026.11.2"
    second_raw = json.dumps(second_payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    first_path.write_bytes(first_raw)
    second_path.write_bytes(second_raw)
    registry, status = load_session_calendar_runtime(
        artifact_path="", expected_sha256="", expected_version="",
        releases=((str(first_path), hashlib.sha256(first_raw).hexdigest(), "2026.11.1"),
                  (str(second_path), hashlib.sha256(second_raw).hexdigest(), "2026.11.2")),
    )
    assert len(registry) == 0
    assert status == {"state": "unavailable", "reason": "release_validation_failed"}


def test_settings_rejects_ambiguous_multi_release_manifest():
    from app.config import _parse_session_calendar_releases
    import pytest
    valid = {"artifact_path": "/data/es.json", "sha256": "a" * 64, "version": "v1"}
    assert _parse_session_calendar_releases(json.dumps([valid])) == (("/data/es.json", "a" * 64, "v1"),)
    with pytest.raises(ValueError):
        _parse_session_calendar_releases(json.dumps([valid, valid]))
    with pytest.raises(ValueError):
        _parse_session_calendar_releases('[{"artifact_path":"/data/es.json","sha256":"bad"}]')
    with pytest.raises(ValueError):
        _parse_session_calendar_releases('[{"artifact_path":"/a","artifact_path":"/b","sha256":"' + "a" * 64 + '","version":"v1"}]')
