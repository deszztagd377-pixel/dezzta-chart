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
        "schema_version": 1,
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
    assert len(application.state.ohlcv_store.load_bars()) == 1


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
