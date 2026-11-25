"""Provider-neutral demand reference counting for deterministic offline use.

This module is deliberately not wired into ProviderManager or any live source.
It supplies a small, testable ownership primitive for future Stage 2 integration.
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Protocol
from uuid import uuid4


@dataclass(frozen=True, slots=True, order=True)
class ProviderDemandKey:
    """Identity of one upstream stream, independent of a chart panel."""

    source: str
    venue: str
    instrument: str
    channel: str

    def __post_init__(self) -> None:
        for name in ("source", "venue", "instrument", "channel"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value or value != value.strip():
                raise ValueError(f"{name} must be a non-empty canonical string")
            if len(value) > 128:
                raise ValueError(f"{name} exceeds 128 characters")


class ProviderDemandAdapter(Protocol):
    """Minimal async lifecycle contract; no data or network API is exposed."""

    async def start(self, key: ProviderDemandKey) -> None: ...

    async def stop(self, key: ProviderDemandKey) -> None: ...


@dataclass(frozen=True, slots=True)
class DemandLease:
    """Opaque ownership token; one lease represents one subscriber/key pair."""

    lease_id: str
    subscriber_id: str
    key: ProviderDemandKey


class ProviderDemandCoordinator:
    """Serialize acquire/release and start/stop each key on 0↔1 transitions.

    Duplicate acquire by the same subscriber for the same key is idempotent.
    Releasing an unknown/already-released lease is a no-op returning False.
    If adapter.stop fails, the final lease is retained so callers can retry;
    the coordinator never reports an upstream as stopped when it is not.
    """

    def __init__(self, adapter: ProviderDemandAdapter) -> None:
        if adapter is None or not callable(getattr(adapter, "start", None)) or not callable(
            getattr(adapter, "stop", None)
        ):
            raise TypeError("adapter must provide async start(key) and stop(key)")
        self._adapter = adapter
        self._lock = asyncio.Lock()
        self._leases_by_id: dict[str, DemandLease] = {}
        self._lease_ids_by_key: dict[ProviderDemandKey, set[str]] = {}
        self._lease_by_owner: dict[tuple[str, ProviderDemandKey], str] = {}

    @staticmethod
    def _validate_subscriber(subscriber_id: str) -> None:
        if (
            not isinstance(subscriber_id, str)
            or not subscriber_id
            or subscriber_id != subscriber_id.strip()
            or len(subscriber_id) > 128
        ):
            raise ValueError("subscriber_id must be a non-empty canonical string")

    async def acquire(self, subscriber_id: str, key: ProviderDemandKey) -> DemandLease:
        self._validate_subscriber(subscriber_id)
        if not isinstance(key, ProviderDemandKey):
            raise TypeError("key must be a ProviderDemandKey")
        owner = (subscriber_id, key)
        async with self._lock:
            existing_id = self._lease_by_owner.get(owner)
            if existing_id is not None:
                return self._leases_by_id[existing_id]

            current = self._lease_ids_by_key.get(key)
            if not current:
                # Do not publish ownership until upstream startup succeeds.
                await self._adapter.start(key)

            lease = DemandLease(uuid4().hex, subscriber_id, key)
            self._leases_by_id[lease.lease_id] = lease
            self._lease_by_owner[owner] = lease.lease_id
            self._lease_ids_by_key.setdefault(key, set()).add(lease.lease_id)
            return lease

    async def release(self, lease: DemandLease | str) -> bool:
        lease_id = lease.lease_id if isinstance(lease, DemandLease) else lease
        if not isinstance(lease_id, str) or not lease_id:
            return False
        async with self._lock:
            current_lease = self._leases_by_id.get(lease_id)
            if current_lease is None:
                return False
            owners = self._lease_ids_by_key[current_lease.key]
            if len(owners) == 1:
                # Preserve the final lease if stop fails; caller can retry.
                await self._adapter.stop(current_lease.key)

            owners.remove(lease_id)
            self._leases_by_id.pop(lease_id, None)
            self._lease_by_owner.pop((current_lease.subscriber_id, current_lease.key), None)
            if not owners:
                self._lease_ids_by_key.pop(current_lease.key, None)
            return True

    def subscriber_count(self, key: ProviderDemandKey) -> int:
        return len(self._lease_ids_by_key.get(key, ()))

    @property
    def active_keys(self) -> tuple[ProviderDemandKey, ...]:
        return tuple(sorted(self._lease_ids_by_key))

    @property
    def active_lease_count(self) -> int:
        return len(self._leases_by_id)


class InMemoryOfflineProviderAdapter:
    """Deterministic test adapter: records lifecycle only and performs no I/O."""

    def __init__(self) -> None:
        self.active: set[ProviderDemandKey] = set()
        self.start_calls: list[ProviderDemandKey] = []
        self.stop_calls: list[ProviderDemandKey] = []
        self.start_error: BaseException | None = None
        self.stop_error: BaseException | None = None

    async def start(self, key: ProviderDemandKey) -> None:
        if self.start_error is not None:
            raise self.start_error
        if key in self.active:
            raise RuntimeError("offline adapter received duplicate start")
        self.start_calls.append(key)
        self.active.add(key)

    async def stop(self, key: ProviderDemandKey) -> None:
        if self.stop_error is not None:
            raise self.stop_error
        if key not in self.active:
            raise RuntimeError("offline adapter received stop for inactive key")
        self.stop_calls.append(key)
        self.active.remove(key)


__all__ = (
    "DemandLease",
    "InMemoryOfflineProviderAdapter",
    "ProviderDemandAdapter",
    "ProviderDemandCoordinator",
    "ProviderDemandKey",
)
