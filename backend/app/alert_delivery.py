"""Lease-safe processing for the durable price-alert trigger outbox.

The sender is an injected adapter. It must deduplicate using event.event_id:
delivery is at-least-once because a sender may succeed just before a worker
loses its lease or crashes before acknowledgement. This module deliberately
does not select a notification provider or start a background scheduler.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from app.alert_store import SQLitePriceAlertStore, PriceAlertTriggerEvent

_SQLITE_INT64_MAX = 9_223_372_036_854_775_807
_DELIVERY_ERROR_CODE = "delivery.error"


@dataclass(frozen=True, slots=True)
class AlertDeliveryBatchResult:
    claimed: int
    delivered: int
    retry_scheduled: int
    terminal_failed: int
    lease_lost: int


def _read_clock_ns(clock_ns: Callable[[], int]) -> int:
    value = clock_ns()
    if (
        not isinstance(value, int)
        or isinstance(value, bool)
        or not 0 <= value <= _SQLITE_INT64_MAX
    ):
        raise ValueError("clock_ns must return a signed 64-bit non-negative integer.")
    return value


def run_alert_delivery_batch(
    store: SQLitePriceAlertStore,
    sender: Callable[[PriceAlertTriggerEvent], None],
    *,
    clock_ns: Callable[[], int],
    lease_duration_ns: int = 30_000_000_000,
    batch_size: int = 100,
    base_retry_delay_ns: int = 5_000_000_000,
    max_retry_delay_ns: int = 300_000_000_000,
    max_attempts: int = 8,
) -> AlertDeliveryBatchResult:
    """Claim and process one bounded batch of pending alert events.

    The sender must treat event.event_id as its idempotency key. Raw sender
    exceptions are intentionally discarded; only a fixed error code is saved.
    A successful send is acknowledged only while its lease remains active.
    Failed sends use capped exponential retry, then enter terminal failure.
    """
    if not callable(sender) or not callable(clock_ns):
        raise ValueError("sender and clock_ns must be callable.")
    positive_values = (
        lease_duration_ns,
        base_retry_delay_ns,
        max_retry_delay_ns,
        max_attempts,
    )
    if any(
        not isinstance(value, int) or isinstance(value, bool) or value < 1
        for value in positive_values
    ):
        raise ValueError("worker timing and attempt limits must be positive integers.")
    if max_retry_delay_ns < base_retry_delay_ns:
        raise ValueError("max_retry_delay_ns must be at least base_retry_delay_ns.")
    if (
        not isinstance(batch_size, int)
        or isinstance(batch_size, bool)
        or not 1 <= batch_size <= 1000
    ):
        raise ValueError("batch_size must be between 1 and 1000.")

    claimed = store.claim_pending_trigger_events(
        now_ns=_read_clock_ns(clock_ns),
        lease_duration_ns=lease_duration_ns,
        limit=batch_size,
    )
    delivered = retry_scheduled = terminal_failed = lease_lost = 0

    for item in claimed:
        event = item.event
        try:
            sender(event)
        except Exception:
            completed_at_ns = _read_clock_ns(clock_ns)
            exhausted = item.attempt_count >= max_attempts
            exponent = min(item.attempt_count - 1, 62)
            retry_delay = min(
                max_retry_delay_ns,
                base_retry_delay_ns * (1 << exponent),
            )
            retry_at_ns = completed_at_ns + retry_delay
            terminal = exhausted or retry_at_ns > _SQLITE_INT64_MAX
            if terminal:
                retry_at_ns = completed_at_ns
            updated = store.reschedule_trigger_event(
                event_id=event.event_id,
                lease_token=item.lease_token,
                now_ns=completed_at_ns,
                next_attempt_ns=retry_at_ns,
                error_code=_DELIVERY_ERROR_CODE,
                terminal=terminal,
            )
            if not updated:
                lease_lost += 1
            elif terminal:
                terminal_failed += 1
            else:
                retry_scheduled += 1
        else:
            acknowledged = store.mark_trigger_event_delivered(
                event_id=event.event_id,
                lease_token=item.lease_token,
                now_ns=_read_clock_ns(clock_ns),
            )
            if acknowledged:
                delivered += 1
            else:
                # A sender may have succeeded after its lease expired. The
                # event can be reclaimed, so the adapter must dedupe event_id.
                lease_lost += 1

    return AlertDeliveryBatchResult(
        claimed=len(claimed),
        delivered=delivered,
        retry_scheduled=retry_scheduled,
        terminal_failed=terminal_failed,
        lease_lost=lease_lost,
    )
