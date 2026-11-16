"""Evidence-backed inventory of market-data provider candidates.

This catalog is intentionally descriptive: it does not instantiate clients,
make network requests, activate feeds, or imply redistribution permission.
Every candidate remains disabled until recurring cost AND intended-use rights
are independently reviewed for the actual DEZZTA CHART deployment.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class CostClass(str, Enum):
    RECURRING_FREE = "recurring_free"
    FREE_TRIAL_OR_CREDIT = "free_trial_or_credit"
    PAID = "paid"
    UNVERIFIED = "unverified"


class RightsStatus(str, Enum):
    APPROVED = "approved"
    RESTRICTED = "restricted"
    UNKNOWN = "unknown"


class FreshnessClass(str, Enum):
    REAL_TIME = "real_time"
    DELAYED_OR_CACHED = "delayed_or_cached"
    DAILY_REFERENCE = "daily_reference"
    PERIODIC_MACRO = "periodic_macro"
    MIXED_OR_PLAN_DEPENDENT = "mixed_or_plan_dependent"


@dataclass(frozen=True)
class ProviderCandidate:
    provider_id: str
    asset_classes: tuple[str, ...]
    data_families: tuple[str, ...]
    freshness: FreshnessClass
    cost_class: CostClass
    rights_status: RightsStatus
    authentication: str
    documented_limit: str
    official_docs_url: str
    caveat: str

    @property
    def eligible_for_zero_cost_baseline(self) -> bool:
        """True only with recurring $0 pricing and approved intended-use rights."""
        return not self.activation_blockers

    @property
    def activation_blockers(self) -> tuple[str, ...]:
        blockers: list[str] = []
        if self.cost_class is not CostClass.RECURRING_FREE:
            blockers.append("recurring_zero_cost_not_proven")
        if self.rights_status is not RightsStatus.APPROVED:
            blockers.append("display_and_redistribution_rights_not_approved")
        if not self.official_docs_url.startswith("https://"):
            blockers.append("official_documentation_missing")
        if not self.documented_limit.strip():
            blockers.append("quota_or_usage_limit_not_documented")
        if not self.asset_classes:
            blockers.append("asset_scope_missing")
        if not self.data_families:
            blockers.append("data_family_scope_missing")
        return tuple(blockers)


# Facts below summarize official public documentation reviewed on 2026-11-16.
# "Candidate" does not mean production approval. Limits and terms can change.
_CANDIDATES = (
    ProviderCandidate(
        provider_id="alpaca_basic",
        asset_classes=("us_equities", "us_etf", "us_options_indicative"),
        data_families=("quotes", "trades", "ohlcv", "instrument_reference"),
        freshness=FreshnessClass.MIXED_OR_PLAN_DEPENDENT,
        cost_class=CostClass.RECURRING_FREE,
        rights_status=RightsStatus.UNKNOWN,
        authentication="account_and_api_key",
        documented_limit=(
            "Equities IEX real-time only; 30 websocket symbols; "
            "200 historical API calls/minute; historical access limited to latest 15 minutes"
        ),
        official_docs_url="https://docs.alpaca.markets/us/docs/about-market-data-api",
        caveat=(
            "Not consolidated all-US-venue coverage. Redistribution/display rights "
            "for this app require separate review."
        ),
    ),
    ProviderCandidate(
        provider_id="alpha_vantage_free",
        asset_classes=("equities_reference", "forex_reference", "crypto_reference"),
        data_families=("ohlcv", "fundamentals", "economic_reference"),
        freshness=FreshnessClass.MIXED_OR_PLAN_DEPENDENT,
        cost_class=CostClass.RECURRING_FREE,
        rights_status=RightsStatus.UNKNOWN,
        authentication="account_and_api_key",
        documented_limit="25 requests/day on the free tier; real-time and 15-minute delayed US stock data are premium",
        official_docs_url="https://www.alphavantage.co/support/api-key/",
        caveat="Not a free real-time US equity feed; confirm display and redistribution terms.",
    ),
    ProviderCandidate(
        provider_id="twelvedata_basic",
        asset_classes=("us_equities", "forex", "crypto"),
        data_families=("ohlcv", "quotes", "technical_indicators"),
        freshness=FreshnessClass.MIXED_OR_PLAN_DEPENDENT,
        cost_class=CostClass.RECURRING_FREE,
        rights_status=RightsStatus.UNKNOWN,
        authentication="account_and_api_key",
        documented_limit="8 API credits; 800 API calls/day shown; websocket allowance is trial-limited",
        official_docs_url="https://twelvedata.com/pricing",
        caveat="Basic plan labels usage as internal non-display; do not assume chart display is permitted.",
    ),
    ProviderCandidate(
        provider_id="coingecko_demo",
        asset_classes=("crypto", "token_reference"),
        data_families=("aggregated_price", "market_cap", "volume", "asset_metadata"),
        freshness=FreshnessClass.DELAYED_OR_CACHED,
        cost_class=CostClass.RECURRING_FREE,
        rights_status=RightsStatus.UNKNOWN,
        authentication="free_demo_account_and_api_key",
        documented_limit="10,000 call credits/month; 100 calls/minute; data freshness from 60 seconds",
        official_docs_url="https://www.coingecko.com/en/api/pricing",
        caveat="Demo tier requires attribution; commercial redistribution rights are not assumed.",
    ),
    ProviderCandidate(
        provider_id="binance_public_market_data",
        asset_classes=("crypto_spot_exchange_specific",),
        data_families=("trades", "quotes", "order_book", "ohlcv", "instrument_reference"),
        freshness=FreshnessClass.REAL_TIME,
        cost_class=CostClass.RECURRING_FREE,
        rights_status=RightsStatus.UNKNOWN,
        authentication="no_api_key_for_market_data_only_endpoints",
        documented_limit="Public REST/WebSocket endpoints; request-weight and IP limits apply and may change",
        official_docs_url="https://github.com/binance/binance-spot-api-docs",
        caveat="Exchange-specific feed, not a consolidated crypto market; review terms before redistribution.",
    ),
    ProviderCandidate(
        provider_id="kraken_public_market_data",
        asset_classes=("crypto_spot_exchange_specific",),
        data_families=("trades", "quotes", "order_book", "ohlcv", "ticker"),
        freshness=FreshnessClass.REAL_TIME,
        cost_class=CostClass.RECURRING_FREE,
        rights_status=RightsStatus.UNKNOWN,
        authentication="no_account_for_public_market_data_endpoints",
        documented_limit="Public endpoints; REST limits are IP/pair dependent",
        official_docs_url="https://support.kraken.com/articles/360000919986-public-endpoint-examples-you-can-try-them-directly-in-a-web-browser-",
        caveat="Exchange-specific feed, not a consolidated crypto market; review terms before redistribution.",
    ),
    ProviderCandidate(
        provider_id="fred",
        asset_classes=("macroeconomic_series",),
        data_families=("economic_time_series", "release_history", "vintage_data"),
        freshness=FreshnessClass.PERIODIC_MACRO,
        cost_class=CostClass.RECURRING_FREE,
        rights_status=RightsStatus.RESTRICTED,
        authentication="free_account_and_api_key",
        documented_limit="120 requests/minute documented; service may impose or change limits",
        official_docs_url="https://fred.stlouisfed.org/docs/api/terms_of_use.html",
        caveat="Not live market prices. Attribution, third-party series rights and API terms apply.",
    ),
    ProviderCandidate(
        provider_id="frankfurter",
        asset_classes=("fx_reference", "currency_reference"),
        data_families=("reference_exchange_rates",),
        freshness=FreshnessClass.DAILY_REFERENCE,
        cost_class=CostClass.RECURRING_FREE,
        rights_status=RightsStatus.UNKNOWN,
        authentication="none",
        documented_limit="Public API without key; rates published once or a few times daily by source institutions",
        official_docs_url="https://frankfurter.dev/",
        caveat="Reference rates, not executable live FX quotes; verify terms for app redistribution.",
    ),
    ProviderCandidate(
        provider_id="world_bank_indicators",
        asset_classes=("macroeconomic_indicators",),
        data_families=("economic_time_series", "country_indicators"),
        freshness=FreshnessClass.PERIODIC_MACRO,
        cost_class=CostClass.RECURRING_FREE,
        rights_status=RightsStatus.UNKNOWN,
        authentication="none_for_indicators_api",
        documented_limit="Nearly 16,000 indicators; API key not required; indicator update frequency varies",
        official_docs_url="https://datahelpdesk.worldbank.org/knowledgebase/articles/889392",
        caveat="Not live market prices; dataset-specific attribution and reuse terms still need review.",
    ),
    ProviderCandidate(
        provider_id="databento",
        asset_classes=("exchange_market_data",),
        data_families=("trades", "quotes", "order_book", "ohlcv", "instrument_definitions"),
        freshness=FreshnessClass.MIXED_OR_PLAN_DEPENDENT,
        cost_class=CostClass.FREE_TRIAL_OR_CREDIT,
        rights_status=RightsStatus.UNKNOWN,
        authentication="account_and_api_key",
        documented_limit="Introductory credits are finite; historical usage is metered and live requires subscription",
        official_docs_url="https://databento.com/pricing/",
        caveat="Trial credit is not recurring free usage; must remain outside the $0 production baseline.",
    ),
)


def provider_candidates() -> tuple[ProviderCandidate, ...]:
    """Return the immutable candidate inventory in stable display order."""
    return _CANDIDATES


def get_provider_candidate(provider_id: str) -> ProviderCandidate | None:
    """Return one exact provider record; unknown IDs are not guessed."""
    normalized = provider_id.strip().lower() if isinstance(provider_id, str) else ""
    return next((item for item in _CANDIDATES if item.provider_id == normalized), None)


def zero_cost_activation_blockers(provider_id: str) -> tuple[str, ...]:
    """Fail closed for unknown providers and candidates without rights approval."""
    candidate = get_provider_candidate(provider_id)
    if candidate is None:
        return ("provider_not_in_reviewed_catalog",)
    return candidate.activation_blockers
