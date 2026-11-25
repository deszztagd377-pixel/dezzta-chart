import asyncio

import pytest

from app.provider_demand import (
    InMemoryOfflineProviderAdapter,
    DemandLease,
    ProviderDemandCoordinator,
    ProviderDemandKey,
)


def key(instrument="EDU-SYNTH-001"):
    return ProviderDemandKey(
        source="offline-fixture",
        venue="synthetic",
        instrument=instrument,
        channel="ohlcv-demo",
    )


def run(coro):
    return asyncio.run(coro)


def test_two_subscribers_share_one_upstream_and_last_release_stops_it():
    async def scenario():
        adapter = InMemoryOfflineProviderAdapter()
        coordinator = ProviderDemandCoordinator(adapter)
        first = await coordinator.acquire("panel-a", key())
        second = await coordinator.acquire("panel-b", key())

        assert first != second
        assert adapter.start_calls == [key()]
        assert coordinator.subscriber_count(key()) == 2
        assert await coordinator.release(first) is True
        assert adapter.active == {key()}
        assert adapter.stop_calls == []
        assert await coordinator.release(second) is True
        assert adapter.active == set()
        assert adapter.stop_calls == [key()]
        assert coordinator.active_lease_count == 0

    run(scenario())


def test_duplicate_acquire_for_same_owner_is_idempotent():
    async def scenario():
        adapter = InMemoryOfflineProviderAdapter()
        coordinator = ProviderDemandCoordinator(adapter)
        first = await coordinator.acquire("panel-a", key())
        duplicate = await coordinator.acquire("panel-a", key())

        assert duplicate == first
        assert coordinator.active_lease_count == 1
        assert coordinator.subscriber_count(key()) == 1
        assert adapter.start_calls == [key()]

    run(scenario())


def test_one_subscriber_can_own_distinct_series_independently():
    async def scenario():
        adapter = InMemoryOfflineProviderAdapter()
        coordinator = ProviderDemandCoordinator(adapter)
        first_key, second_key = key("SYNTH-A"), key("SYNTH-B")
        first = await coordinator.acquire("panel-a", first_key)
        second = await coordinator.acquire("panel-a", second_key)

        assert set(adapter.start_calls) == {first_key, second_key}
        assert await coordinator.release(first) is True
        assert adapter.active == {second_key}
        assert coordinator.subscriber_count(second_key) == 1
        assert await coordinator.release(second) is True

    run(scenario())


def test_unknown_or_already_released_lease_is_a_noop():
    async def scenario():
        adapter = InMemoryOfflineProviderAdapter()
        coordinator = ProviderDemandCoordinator(adapter)
        lease = await coordinator.acquire("panel-a", key())

        assert await coordinator.release("unknown-lease") is False
        assert await coordinator.release(lease) is True
        assert await coordinator.release(lease) is False
        assert coordinator.active_lease_count == 0

    run(scenario())


def test_start_failure_does_not_publish_a_lease_or_active_key():
    async def scenario():
        adapter = InMemoryOfflineProviderAdapter()
        adapter.start_error = RuntimeError("synthetic start failure")
        coordinator = ProviderDemandCoordinator(adapter)

        with pytest.raises(RuntimeError, match="synthetic start failure"):
            await coordinator.acquire("panel-a", key())

        assert coordinator.active_lease_count == 0
        assert coordinator.active_keys == ()
        assert adapter.active == set()

    run(scenario())


def test_failed_last_release_retains_lease_for_safe_retry():
    async def scenario():
        adapter = InMemoryOfflineProviderAdapter()
        coordinator = ProviderDemandCoordinator(adapter)
        lease = await coordinator.acquire("panel-a", key())
        adapter.stop_error = RuntimeError("synthetic stop failure")

        with pytest.raises(RuntimeError, match="synthetic stop failure"):
            await coordinator.release(lease)

        assert coordinator.active_lease_count == 1
        assert coordinator.subscriber_count(key()) == 1
        assert adapter.active == {key()}

        adapter.stop_error = None
        assert await coordinator.release(lease) is True
        assert coordinator.active_lease_count == 0
        assert adapter.active == set()
        assert adapter.stop_calls == [key()]

    run(scenario())


def test_concurrent_acquires_start_exactly_once():
    async def scenario():
        adapter = InMemoryOfflineProviderAdapter()
        coordinator = ProviderDemandCoordinator(adapter)
        leases = await asyncio.gather(
            coordinator.acquire("panel-a", key()),
            coordinator.acquire("panel-b", key()),
            coordinator.acquire("panel-c", key()),
        )

        assert len({lease.lease_id for lease in leases}) == 3
        assert adapter.start_calls == [key()]
        assert coordinator.subscriber_count(key()) == 3
        await asyncio.gather(*(coordinator.release(lease) for lease in leases))
        assert adapter.stop_calls == [key()]
        assert adapter.active == set()

    run(scenario())


@pytest.mark.parametrize(
    "fields",
    [
        {"source": "", "venue": "synthetic", "instrument": "A", "channel": "ohlcv"},
        {"source": "source", "venue": " synthetic", "instrument": "A", "channel": "ohlcv"},
        {"source": "source", "venue": "venue", "instrument": "A" * 129, "channel": "ohlcv"},
    ],
)
def test_demand_key_rejects_noncanonical_or_oversized_fields(fields):
    with pytest.raises(ValueError):
        ProviderDemandKey(**fields)


@pytest.mark.parametrize("subscriber_id", ["", " panel-a", "x" * 129, None])
def test_acquire_rejects_invalid_subscriber_identity(subscriber_id):
    async def scenario():
        coordinator = ProviderDemandCoordinator(InMemoryOfflineProviderAdapter())
        with pytest.raises(ValueError):
            await coordinator.acquire(subscriber_id, key())

    run(scenario())


def test_release_rejects_forged_lease_object_without_releasing_real_owner():
    async def scenario():
        adapter = InMemoryOfflineProviderAdapter()
        coordinator = ProviderDemandCoordinator(adapter)
        original = await coordinator.acquire("panel-a", key())
        forged = DemandLease(
            lease_id=original.lease_id,
            subscriber_id="panel-b",
            key=key("EDU-SYNTH-OTHER"),
        )

        assert await coordinator.release(forged) is False
        assert coordinator.active_lease_count == 1
        assert coordinator.subscriber_count(key()) == 1
        assert adapter.active == {key()}

        assert await coordinator.release(original) is True
        assert coordinator.active_lease_count == 0
        assert adapter.active == set()

    run(scenario())


def test_release_rejects_non_lease_non_string_values():
    async def scenario():
        adapter = InMemoryOfflineProviderAdapter()
        coordinator = ProviderDemandCoordinator(adapter)
        lease = await coordinator.acquire("panel-a", key())

        assert await coordinator.release(None) is False
        assert await coordinator.release(123) is False
        assert coordinator.active_lease_count == 1
        assert await coordinator.release(lease) is True

    run(scenario())
