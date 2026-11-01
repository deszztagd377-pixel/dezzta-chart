"""Validated instrument-definition catalog for supported futures roots.

This module is provider-neutral: it accepts normalized definition mappings and
never invents contract months. Only outright futures with a recognized expiry
are catalogued; spreads and unknown symbols are excluded.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date, datetime, timezone
import re
from typing import Any, Iterable, Mapping

SUPPORTED_PRODUCTS: dict[str, str] = {
    "ES": "E-mini S&P 500 Futures",
    "NQ": "E-mini Nasdaq-100 Futures",
    "GC": "Gold Futures",
}

# CME month codes: F G H J K M N Q U V X Z.
_CONTRACT_SYMBOL = re.compile(r"^(ES|NQ|GC)[FGHJKMNQUVXZ](?:\\d{1,2})$")


class InvalidInstrumentDefinition(ValueError):
    """Raised when a provider definition cannot be safely normalized."""


def _nanoseconds_to_iso_date(value: int) -> str:
    seconds = value // 1_000_000_000
    return datetime.fromtimestamp(seconds, tz=timezone.utc).date().isoformat()


def _fixed_point_to_decimal(value: Any) -> str:
    raw = int(value)
    negative = raw < 0
    absolute = abs(raw)
    whole, fraction = divmod(absolute, 1_000_000_000)
    fractional = str(fraction).rjust(9, "0").rstrip("0")
    result = f"{whole}.{fractional}" if fractional else str(whole)
    return f"-{result}" if negative and absolute else result


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
        try:
            if isinstance(expiration_value, datetime):
                expiration = expiration_value.date().isoformat()
            elif isinstance(expiration_value, date):
                expiration = expiration_value.isoformat()
            elif isinstance(expiration_value, int):
                if expiration_value <= 0:
                    raise ValueError("Expiration timestamp must be positive.")
                expiration = _nanoseconds_to_iso_date(expiration_value)
            elif expiration_value:
                expiration_text = str(expiration_value).strip()
                if expiration_text.isdigit() and len(expiration_text) >= 15:
                    expiration = _nanoseconds_to_iso_date(int(expiration_text))
                else:
                    expiration = date.fromisoformat(expiration_text[:10]).isoformat()
            else:
                raise ValueError("Contract expiration is required.")
        except (OverflowError, OSError, ValueError) as exc:
            raise InvalidInstrumentDefinition("Invalid contract expiration.") from exc

        try:
            instrument_id = int(definition["instrument_id"])
            publisher_id = int(definition["publisher_id"])
            ts_event = int(definition["ts_event"])
        except (KeyError, TypeError, ValueError) as exc:
            raise InvalidInstrumentDefinition(
                "instrument_id, publisher_id, and ts_event are required integers."
            ) from exc

        if instrument_id < 0 or publisher_id < 0 or ts_event < 0:
            raise InvalidInstrumentDefinition(
                "Provider identifiers and timestamp must be non-negative."
            )

        root = match.group(1)
        increment = definition.get("min_price_increment")
        currency = definition.get("currency")

        try:
            normalized_increment = (
                _fixed_point_to_decimal(increment) if increment is not None else None
            )
        except (TypeError, ValueError, OverflowError) as exc:
            raise InvalidInstrumentDefinition("Invalid minimum price increment.") from exc

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
            min_price_increment=normalized_increment,
            definition_ts_event_ns=str(ts_event),
        )


class InstrumentCatalog:
    """In-memory catalog with snapshot replacement and ordered lifecycle events.

    Contract identity is scoped by dataset, publisher, and instrument ID.
    Definition timestamps are used to stop delayed updates from overwriting
    newer metadata and to stop delayed upserts from resurrecting deleted rows.
    """

    def __init__(self) -> None:
        self._contracts: dict[tuple[str, int, int], FuturesInstrument] = {}
        self._tombstones: dict[tuple[str, int, int], int] = {}

    @staticmethod
    def _key(contract: FuturesInstrument) -> tuple[str, int, int]:
        return (contract.dataset, contract.publisher_id, contract.instrument_id)

    def replace_definitions(
        self,
        definitions: Iterable[Mapping[str, Any]],
        *,
        dataset: str = "GLBX.MDP3",
    ) -> int:
        """Replace the complete snapshot; omitted contracts become stale/removed.

        Invalid rows are counted and excluded. The new snapshot is assembled
        before assignment, so callers never observe a partially replaced catalog.
        """
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

            key = self._key(contract)
            previous = next_contracts.get(key)
            if previous is None or int(contract.definition_ts_event_ns) > int(
                previous.definition_ts_event_ns
            ):
                next_contracts[key] = contract
            else:
                rejected += 1

        self._contracts = next_contracts
        # A complete authoritative snapshot supersedes the incremental tombstones.
        self._tombstones.clear()
        return rejected

    def upsert_definition(
        self,
        definition: Mapping[str, Any],
        *,
        dataset: str = "GLBX.MDP3",
    ) -> bool:
        """Insert/update one contract unless its event is stale or tombstoned."""
        contract = FuturesInstrument.from_provider_definition(
            definition,
            dataset=dataset,
        )
        key = self._key(contract)
        event_ts = int(contract.definition_ts_event_ns)
        tombstone_ts = self._tombstones.get(key)
        if tombstone_ts is not None and event_ts <= tombstone_ts:
            return False

        current = self._contracts.get(key)
        if current is not None and event_ts <= int(current.definition_ts_event_ns):
            return False

        self._contracts[key] = contract
        self._tombstones.pop(key, None)
        return True

    def delete_definition(
        self,
        *,
        publisher_id: int,
        instrument_id: int,
        event_ts_ns: int,
        dataset: str = "GLBX.MDP3",
    ) -> bool:
        """Apply a timestamped deletion; stale deletes cannot remove newer rows.

        Tombstones are retained so a delayed older upsert cannot resurrect a
        contract after its deletion event.
        """
        if publisher_id < 0 or instrument_id < 0 or event_ts_ns < 0:
            raise ValueError("Deletion identifiers and timestamp must be non-negative.")

        key = (dataset, publisher_id, instrument_id)
        current = self._contracts.get(key)
        previous_tombstone = self._tombstones.get(key)
        newest_known = max(
            int(current.definition_ts_event_ns) if current else -1,
            previous_tombstone if previous_tombstone is not None else -1,
        )
        if event_ts_ns < newest_known:
            return False

        self._contracts.pop(key, None)
        self._tombstones[key] = event_ts_ns
        return True

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
