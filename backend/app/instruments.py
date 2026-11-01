"""Validated instrument-definition catalog for supported futures roots.

This module is provider-neutral: it accepts normalized definition mappings and
never invents contract months. Only outright futures with a recognized expiry
are catalogued; spreads and unknown symbols are excluded.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date, datetime
import re
from typing import Any, Iterable, Mapping

SUPPORTED_PRODUCTS: dict[str, str] = {
    "ES": "E-mini S&P 500 Futures",
    "NQ": "E-mini Nasdaq-100 Futures",
    "GC": "Gold Futures",
}

# CME month codes: F G H J K M N Q U V X Z.
_CONTRACT_SYMBOL = re.compile(r"^(ES|NQ|GC)[FGHJKMNQUVXZ](?:\d{1,2})$")


class InvalidInstrumentDefinition(ValueError):
    """Raised when a provider definition cannot be safely normalized."""


@dataclass(frozen=True, slots=True)
class FuturesInstrument:
    root: str
    product_name: str
    dataset: str
    raw_symbol: str
    instrument_id: int
    publisher_id: int
    instrument_class: str
    expiration: str
    currency: str | None
    min_price_increment: str | None
    definition_ts_event_ns: str

    @classmethod
    def from_provider_definition(
        cls,
        definition: Mapping[str, Any],
        *,
        dataset: str = "GLBX.MDP3",
    ) -> "FuturesInstrument":
        raw_symbol = str(definition.get("raw_symbol", "")).strip().upper()
        match = _CONTRACT_SYMBOL.fullmatch(raw_symbol)
        if not match:
            raise InvalidInstrumentDefinition("Unsupported outright futures symbol.")

        instrument_class = str(definition.get("instrument_class", "")).strip().upper()
        if instrument_class != "F":
            raise InvalidInstrumentDefinition("Only outright futures are supported.")

        expiration_value = definition.get("expiration")
        if isinstance(expiration_value, datetime):
            expiration = expiration_value.date().isoformat()
        elif isinstance(expiration_value, date):
            expiration = expiration_value.isoformat()
        elif expiration_value:
            expiration = str(expiration_value)[:10]
            try:
                date.fromisoformat(expiration)
            except ValueError as exc:
                raise InvalidInstrumentDefinition("Invalid contract expiration.") from exc
        else:
            raise InvalidInstrumentDefinition("Contract expiration is required.")

        try:
            instrument_id = int(definition["instrument_id"])
            publisher_id = int(definition["publisher_id"])
            ts_event = int(definition["ts_event"])
        except (KeyError, TypeError, ValueError) as exc:
            raise InvalidInstrumentDefinition(
                "instrument_id, publisher_id, and ts_event are required integers."
            ) from exc

        if instrument_id < 0 or publisher_id < 0 or ts_event < 0:
            raise InvalidInstrumentDefinition("Provider identifiers and timestamp must be non-negative.")

        root = match.group(1)
        increment = definition.get("min_price_increment")
        currency = definition.get("currency")

        return cls(
            root=root,
            product_name=SUPPORTED_PRODUCTS[root],
            dataset=dataset,
            raw_symbol=raw_symbol,
            instrument_id=instrument_id,
            publisher_id=publisher_id,
            instrument_class=instrument_class,
            expiration=expiration,
            currency=str(currency) if currency else None,
            min_price_increment=str(increment) if increment is not None else None,
            definition_ts_event_ns=str(ts_event),
        )


class InstrumentCatalog:
    """In-memory, replaceable snapshot of verified outright contract definitions."""

    def __init__(self) -> None:
        self._contracts: dict[tuple[str, int, int], FuturesInstrument] = {}

    def replace_definitions(
        self,
        definitions: Iterable[Mapping[str, Any]],
        *,
        dataset: str = "GLBX.MDP3",
    ) -> int:
        next_contracts: dict[tuple[str, int, int], FuturesInstrument] = {}
        rejected = 0
        for definition in definitions:
            try:
                contract = FuturesInstrument.from_provider_definition(
                    definition,
                    dataset=dataset,
                )
            except InvalidInstrumentDefinition:
                rejected += 1
                continue
            key = (contract.dataset, contract.publisher_id, contract.instrument_id)
            next_contracts[key] = contract
        self._contracts = next_contracts
        return rejected

    def list_contracts(self, root: str | None = None) -> list[dict[str, Any]]:
        normalized_root = root.upper() if root else None
        if normalized_root and normalized_root not in SUPPORTED_PRODUCTS:
            raise ValueError("Unsupported product root.")

        contracts = [
            contract
            for contract in self._contracts.values()
            if normalized_root is None or contract.root == normalized_root
        ]
        contracts.sort(key=lambda item: (item.root, item.expiration, item.raw_symbol))
        return [asdict(contract) for contract in contracts]

    def snapshot(self) -> dict[str, Any]:
        contracts = self.list_contracts()
        return {
            "dataset": "GLBX.MDP3",
            "state": "definitions_unavailable" if not contracts else "ready",
            "supported_products": [
                {"root": root, "product_name": name}
                for root, name in SUPPORTED_PRODUCTS.items()
            ],
            "contract_count": len(contracts),
            "contracts": contracts,
            "selection_policy": "No contract is auto-selected; expiry and rollover policy require explicit validation.",
        }
