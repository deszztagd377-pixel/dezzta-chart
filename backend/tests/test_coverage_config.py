from app.config import Settings
from app.coverage import CoverageTracker


def test_coverage_merges_carves_gaps_and_never_claims_unknown_as_covered():
    c = CoverageTracker()
    c.add_covered("s", 0, 10)
    c.add_covered("s", 10, 20)
    assert c.intervals("s") == [(0, 20)]
    assert c.status("s", 5, 15) == "covered"
    c.add_gap("s", 8, 12)
    assert c.intervals("s") == [(0, 8), (12, 20)]
    assert c.status("s", 5, 15) == "partial"
    assert c.status("s", 30, 40) == "unknown"
    assert c.status("other", 0, 5) == "unknown"


def test_coverage_interval_count_is_bounded_and_reports_truncation():
    c = CoverageTracker(max_intervals=3)
    for i in range(6):
        c.add_covered("s", i * 10, i * 10 + 5)
    assert len(c.intervals("s")) == 3 and c.truncated == 3


def test_settings_defaults_are_safe_and_key_is_never_in_repr():
    s = Settings(app_env="x", market_data_ws_token="t", cors_allowed_origins=())
    assert s.databento_api_key == "" and not s.provider_configured
    assert not s.databento_live_enabled and not s.databento_historical_enabled
    secret = "db-SECRETSECRETSECRETSECRET123456"
    s2 = Settings(app_env="x", market_data_ws_token="t", cors_allowed_origins=(), databento_api_key=secret)
    assert secret not in repr(s2) and s2.provider_configured


def test_settings_from_environment_parses_flags_and_ignores_garbage():
    import os
    saved = dict(os.environ)
    try:
        os.environ.update({
            "DATABENTO_LIVE_ENABLED": "TRUE", "DATABENTO_LIVE_SYMBOLS": "ESZ6, NQZ6,",
            "OHLCV_QUEUE_MAX": "not-a-number", "INSTRUMENT_ROOTS": "es,cl",
        })
        s = Settings.from_environment()
    finally:
        os.environ.clear()
        os.environ.update(saved)
    assert s.databento_live_enabled and s.databento_live_symbols == ("ESZ6", "NQZ6")
    assert s.ohlcv_queue_max == 10_000  # invalid value falls back to the safe default
    assert s.allowed_roots == ("ES", "CL")