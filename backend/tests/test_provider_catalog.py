from app.provider_catalog import (
    CostClass,
    FreshnessClass,
    RightsStatus,
    get_provider_candidate,
    provider_candidates,
    zero_cost_activation_blockers,
)


def test_catalog_is_nonempty_and_provider_ids_are_unique():
    candidates = provider_candidates()
    assert candidates
    ids = [item.provider_id for item in candidates]
    assert len(ids) == len(set(ids))


def test_unknown_provider_fails_closed():
    assert zero_cost_activation_blockers("not-a-provider") == (
        "provider_not_in_reviewed_catalog",
    )


def test_no_candidate_is_activated_without_rights_approval():
    assert all(not item.eligible_for_zero_cost_baseline for item in provider_candidates())


def test_trial_credit_is_never_classified_as_recurring_free():
    databento = get_provider_candidate("databento")
    assert databento is not None
    assert databento.cost_class is CostClass.FREE_TRIAL_OR_CREDIT
    assert "recurring_zero_cost_not_proven" in databento.activation_blockers


def test_fred_is_macro_periodic_and_has_restricted_rights_review():
    fred = get_provider_candidate("fred")
    assert fred is not None
    assert fred.freshness is FreshnessClass.PERIODIC_MACRO
    assert fred.rights_status is RightsStatus.RESTRICTED
    assert "display_and_redistribution_rights_not_approved" in fred.activation_blockers


def test_exchange_specific_public_data_is_not_marked_as_consolidated_market():
    binance = get_provider_candidate("binance_public_market_data")
    kraken = get_provider_candidate("kraken_public_market_data")
    assert binance is not None and kraken is not None
    assert binance.asset_classes == ("crypto_spot_exchange_specific",)
    assert kraken.asset_classes == ("crypto_spot_exchange_specific",)
    assert binance.rights_status is RightsStatus.UNKNOWN
    assert kraken.rights_status is RightsStatus.UNKNOWN


def test_frankfurter_is_reference_data_not_live_executable_quotes():
    item = get_provider_candidate("frankfurter")
    assert item is not None
    assert item.freshness is FreshnessClass.DAILY_REFERENCE
    assert "not executable live FX quotes" in item.caveat


def test_alpaca_free_feed_does_not_claim_all_us_venues():
    item = get_provider_candidate("alpaca_basic")
    assert item is not None
    assert "IEX" in item.documented_limit
    assert "Not consolidated all-US-venue coverage" in item.caveat


def test_provider_lookup_is_exact_and_case_normalized():
    assert get_provider_candidate("ALPACA_BASIC") == get_provider_candidate("alpaca_basic")
    assert get_provider_candidate("alpaca") is None
