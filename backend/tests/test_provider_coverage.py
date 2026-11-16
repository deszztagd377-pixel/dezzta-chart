from app.provider_catalog import (
    CostClass,
    FreshnessClass,
    ProviderCandidate,
    RightsStatus,
    provider_candidates,
)
from app.provider_coverage import ProviderInstrumentMapping, build_coverage_report


def _approved_candidate(provider_id: str) -> ProviderCandidate:
    return ProviderCandidate(
        provider_id=provider_id,
        asset_classes=("crypto_spot_exchange_specific",),
        data_families=("ohlcv",),
        freshness=FreshnessClass.REAL_TIME,
        cost_class=CostClass.RECURRING_FREE,
        rights_status=RightsStatus.APPROVED,
        authentication="none",
        documented_limit="documented test quota",
        official_docs_url="https://example.com/docs",
        caveat="synthetic unit-test fixture only",
    )


def _mapping(provider: str, instrument: str, venue: str = "venue-x"):
    return ProviderInstrumentMapping(
        provider_id=provider,
        instrument_id=instrument,
        venue=venue,
        data_family="ohlcv",
        evidence_ref="test-fixture:approved-mapping",
    )


def test_coverage_union_counts_complementary_provider_instruments():
    report = build_coverage_report(
        ["BTC-USD", "ETH-USD", "SOL-USD"],
        [_mapping("provider-a", "BTC-USD"), _mapping("provider-b", "ETH-USD")],
        [_approved_candidate("provider-a"), _approved_candidate("provider-b")],
    )
    assert report.covered == ("BTC-USD", "ETH-USD")
    assert report.uncovered == ("SOL-USD",)
    assert report.redundant == ()
    assert report.eligible_mapping_count == 2
    assert report.coverage_ratio == 2 / 3


def test_redundancy_is_explicit_and_never_blends_provider_data():
    report = build_coverage_report(
        ["BTC-USD"],
        [_mapping("provider-a", "BTC-USD"), _mapping("provider-b", "BTC-USD")],
        [_approved_candidate("provider-a"), _approved_candidate("provider-b")],
    )
    assert report.covered == ("BTC-USD",)
    assert report.redundant == ("BTC-USD",)
    assert report.provider_counts == (("provider-a", 1), ("provider-b", 1))


def test_existing_catalog_candidates_are_rejected_until_rights_approved():
    report = build_coverage_report(
        ["BTC-USD"],
        [_mapping("binance_public_market_data", "BTC-USD")],
        provider_candidates(),
    )
    assert report.covered == ()
    assert report.uncovered == ("BTC-USD",)
    assert report.eligible_mapping_count == 0
    assert report.rejected_mapping_count == 1


def test_unknown_provider_and_out_of_watchlist_mapping_fail_closed():
    report = build_coverage_report(
        ["BTC-USD"],
        [_mapping("unknown-provider", "BTC-USD"), _mapping("provider-a", "ETH-USD")],
        [_approved_candidate("provider-a")],
    )
    assert report.covered == ()
    assert report.uncovered == ("BTC-USD",)
    assert report.rejected_mapping_count == 2


def test_duplicate_provider_instrument_venue_family_mapping_is_counted_once():
    duplicate = _mapping("provider-a", "BTC-USD")
    report = build_coverage_report(
        ["BTC-USD"],
        [duplicate, duplicate],
        [_approved_candidate("provider-a")],
    )
    assert report.eligible_mapping_count == 1
    assert report.rejected_mapping_count == 1


def test_mapping_without_evidence_reference_is_rejected():
    mapping = ProviderInstrumentMapping(
        provider_id="provider-a",
        instrument_id="BTC-USD",
        venue="venue-x",
        data_family="ohlcv",
        evidence_ref=" ",
    )
    report = build_coverage_report(
        ["BTC-USD"], [mapping], [_approved_candidate("provider-a")]
    )
    assert report.covered == ()
    assert report.rejected_mapping_count == 1


def test_empty_watchlist_has_complete_zero_work_coverage():
    report = build_coverage_report([], [], [])
    assert report.coverage_ratio == 1.0
    assert report.covered == report.uncovered == report.redundant == ()
