import asyncio

import pytest

from app.provider_demand import (
    InMemoryOfflineProviderAdapter,
    DemandLease,
    ProviderDemandCoordinator,
    ProviderDemandKey,
)


def key(instrument="EDU-SYNTH-001", *, dataset="offline-fixture-dataset", symbology="raw_symbol"):
    return ProviderDemandKey(
        source="offline-fixture",
        venue="synthetic",
        dataset=dataset,
        instrument=instrument,
        symbology=symbology,
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




def test_dataset_and_symbology_are_part_of_upstream_identity():
    async def scenario():
        adapter = InMemoryOfflineProviderAdapter()
        coordinator = ProviderDemandCoordinator(adapter)
        alternate_dataset = key(dataset="offline-fixture-alt")
        alternate_symbology = key(symbology="instrument_id")
        first = await coordinator.acquire("panel-a", key())
        second = await coordinator.acquire("panel-a", alternate_dataset)
        third = await coordinator.acquire("panel-a", alternate_symbology)

        assert len({first.key, second.key, third.key}) == 3
        assert adapter.start_calls == [key(), alternate_dataset, alternate_symbology]
        assert coordinator.active_lease_count == 3
        assert coordinator.subscriber_count(key()) == 1
        assert coordinator.subscriber_count(alternate_dataset) == 1
        assert coordinator.subscriber_count(alternate_symbology) == 1

        assert await coordinator.release(second) is True
        assert adapter.active == {key(), alternate_symbology}
        assert await coordinator.release(first) is True
        assert await coordinator.release(third) is True
        assert adapter.active == set()
        assert len(adapter.stop_calls) == 3

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


def test_release_with_retry_recovers_from_transient_stop_failure():
    async def scenario():
        class FlakyAdapter(InMemoryOfflineProviderAdapter):
            def __init__(self):
                super().__init__()
                self.failures_remaining = 1

            async def stop(self, demand_key):
                if self.failures_remaining:
                    self.failures_remaining -= 1
                    raise RuntimeError("transient stop failure")
                await super().stop(demand_key)

        adapter = FlakyAdapter()
        coordinator = ProviderDemandCoordinator(adapter)
        lease = await coordinator.acquire("panel-a", key())

        assert await coordinator.release_with_retry(
            lease, attempts=3, initial_delay=0
        ) is True
        assert coordinator.active_lease_count == 0
        assert adapter.active == set()
        assert adapter.stop_calls == [key()]

    run(scenario())


def test_release_with_retry_preserves_lease_after_exhaustion():
    async def scenario():
        adapter = InMemoryOfflineProviderAdapter()
        coordinator = ProviderDemandCoordinator(adapter)
        lease = await coordinator.acquire("panel-a", key())
        adapter.stop_error = RuntimeError("persistent stop failure")

        with pytest.raises(RuntimeError, match="persistent stop failure"):
            await coordinator.release_with_retry(
                lease, attempts=2, initial_delay=0
            )

        assert coordinator.active_lease_count == 1
        assert coordinator.subscriber_count(key()) == 1
        assert adapter.active == {key()}
        assert adapter.stop_calls == []

    run(scenario())


def test_cancelled_retry_backoff_is_queued_for_reconciliation():
    async def scenario():
        class FailFirstStopAdapter(InMemoryOfflineProviderAdapter):
            def __init__(self):
                super().__init__()
                self.first_failure = True
                self.first_stop_failed = asyncio.Event()

            async def stop(self, demand_key):
                if self.first_failure:
                    self.first_failure = False
                    self.first_stop_failed.set()
                    raise RuntimeError("temporary stop failure")
                await super().stop(demand_key)

        adapter = FailFirstStopAdapter()
        coordinator = ProviderDemandCoordinator(adapter)
        lease = await coordinator.acquire("panel-a", key())
        release_task = asyncio.create_task(
            coordinator.release_with_retry(
                lease, attempts=3, initial_delay=1.0
            )
        )
        await adapter.first_stop_failed.wait()
        await asyncio.sleep(0)
        release_task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await release_task

        assert coordinator.active_lease_count == 1
        assert coordinator.pending_release_count == 1
        assert await coordinator.retry_pending_releases() == 1
        assert coordinator.active_lease_count == 0
        assert adapter.active == set()

    run(scenario())


def test_pending_release_reconciliation_recovers_persistent_stop_failure():
    async def scenario():
        adapter = InMemoryOfflineProviderAdapter()
        coordinator = ProviderDemandCoordinator(adapter)
        lease = await coordinator.acquire("panel-a", key())
        adapter.stop_error = RuntimeError("persistent stop failure")

        with pytest.raises(RuntimeError, match="persistent stop failure"):
            await coordinator.release_with_retry(
                lease, attempts=2, initial_delay=0
            )

        assert coordinator.pending_release_count == 1
        assert coordinator.active_lease_count == 1

        adapter.stop_error = None
        assert await coordinator.retry_pending_releases() == 1
        assert coordinator.pending_release_count == 0
        assert coordinator.active_lease_count == 0
        assert adapter.active == set()
        assert adapter.stop_calls == [key()]

    run(scenario())


def test_cancelled_release_is_queued_for_reconciliation():
    async def scenario():
        class BlockingStopAdapter(InMemoryOfflineProviderAdapter):
            def __init__(self):
                super().__init__()
                self.stop_started = asyncio.Event()
                self.allow_stop = asyncio.Event()

            async def stop(self, demand_key):
                self.stop_started.set()
                await self.allow_stop.wait()
                await super().stop(demand_key)

        adapter = BlockingStopAdapter()
        coordinator = ProviderDemandCoordinator(adapter)
        lease = await coordinator.acquire("panel-a", key())
        release_task = asyncio.create_task(
            coordinator.release_with_retry(lease, attempts=3, initial_delay=0)
        )
        await adapter.stop_started.wait()
        release_task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await release_task

        assert coordinator.active_lease_count == 1
        assert coordinator.pending_release_count == 1
        adapter.allow_stop.set()
        assert await coordinator.retry_pending_releases() == 1
        assert coordinator.active_lease_count == 0
        assert coordinator.pending_release_count == 0
        assert adapter.active == set()

    run(scenario())


def test_pending_release_reconciliation_keeps_failed_lease_queued():
    async def scenario():
        adapter = InMemoryOfflineProviderAdapter()
        coordinator = ProviderDemandCoordinator(adapter)
        lease = await coordinator.acquire("panel-a", key())
        adapter.stop_error = RuntimeError("still unavailable")

        with pytest.raises(RuntimeError, match="still unavailable"):
            await coordinator.release_with_retry(
                lease, attempts=1, initial_delay=0
            )

        assert await coordinator.retry_pending_releases() == 0
        assert coordinator.pending_release_count == 1
        assert coordinator.active_lease_count == 1

    run(scenario())


def test_release_with_retry_rejects_invalid_retry_policy():
    async def scenario():
        coordinator = ProviderDemandCoordinator(InMemoryOfflineProviderAdapter())
        with pytest.raises(ValueError, match="attempts"):
            await coordinator.release_with_retry("lease", attempts=0)
        with pytest.raises(ValueError, match="attempts"):
            await coordinator.release_with_retry("lease", attempts=6)
        with pytest.raises(ValueError, match="initial_delay"):
            await coordinator.release_with_retry("lease", initial_delay=-1)
        with pytest.raises(ValueError, match="initial_delay"):
            await coordinator.release_with_retry("lease", initial_delay=1.01)
        with pytest.raises(ValueError, match="initial_delay"):
            await coordinator.release_with_retry("lease", initial_delay=float("inf"))
        with pytest.raises(ValueError, match="initial_delay"):
            await coordinator.release_with_retry("lease", initial_delay=float("nan"))

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
        {"source": "", "venue": "synthetic", "dataset": "dataset", "instrument": "A", "symbology": "raw", "channel": "ohlcv"},
        {"source": "source", "venue": " synthetic", "dataset": "dataset", "instrument": "A", "symbology": "raw", "channel": "ohlcv"},
        {"source": "source", "venue": "venue", "dataset": "dataset", "instrument": "A" * 129, "symbology": "raw", "channel": "ohlcv"},
        {"source": "source", "venue": "venue", "dataset": " dataset", "instrument": "A", "symbology": "raw", "channel": "ohlcv"},
        {"source": "source", "venue": "venue", "dataset": "D" * 129, "instrument": "A", "symbology": "raw", "channel": "ohlcv"},
        {"source": "source", "venue": "venue", "dataset": "dataset", "instrument": "A", "symbology": " raw", "channel": "ohlcv"},
        {"source": "source", "venue": "venue", "dataset": "dataset", "instrument": "A", "symbology": "S" * 129, "channel": "ohlcv"},
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

def test_concurrent_duplicate_releases_stop_upstream_exactly_once():
    async def scenario():
        adapter = InMemoryOfflineProviderAdapter()
        coordinator = ProviderDemandCoordinator(adapter)
        lease = await coordinator.acquire("panel-a", key())

        results = await asyncio.gather(
            *(coordinator.release(lease) for _ in range(32))
        )

        assert results.count(True) == 1
        assert results.count(False) == 31
        assert adapter.start_calls == [key()]
        assert adapter.stop_calls == [key()]
        assert adapter.active == set()
        assert coordinator.active_lease_count == 0
        assert coordinator.subscriber_count(key()) == 0
        assert coordinator.pending_release_count == 0

    run(scenario())


def test_concurrent_final_releases_stop_shared_upstream_once():
    async def scenario():
        adapter = InMemoryOfflineProviderAdapter()
        coordinator = ProviderDemandCoordinator(adapter)
        leases = [
            await coordinator.acquire(f"panel-{index}", key())
            for index in range(16)
        ]

        results = await asyncio.gather(
            *(coordinator.release(lease) for lease in leases)
        )

        assert results == [True] * 16
        assert adapter.start_calls == [key()]
        assert adapter.stop_calls == [key()]
        assert adapter.active == set()
        assert coordinator.active_lease_count == 0
        assert coordinator.subscriber_count(key()) == 0
        assert coordinator.active_keys == ()
        assert coordinator.pending_release_count == 0

    run(scenario())

