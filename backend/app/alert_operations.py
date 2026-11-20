"""Sanitized, local-only operator alerts for the price-alert delivery worker.

The reporter writes transition-based JSON records to the supplied application
logger. It never contacts a notification provider and never logs event payloads,
owner identifiers, registration tokens, exception messages, or credentials.
"""
from __future__ import annotations

import json
import logging
from typing import Any


class LocalAlertReporter:
    """Emit bounded local operational alerts without external services."""

    def __init__(self, logger: logging.Logger, incident_store=None) -> None:
        if not isinstance(logger, logging.Logger):
            raise TypeError("logger must be a logging.Logger.")
        self._logger = logger
        self._incident_store = incident_store
        self._last_state: tuple[Any, ...] | None = None

    @staticmethod
    def _validate_counts(**counts: int) -> None:
        if any(
            not isinstance(value, int) or isinstance(value, bool) or value < 0
            for value in counts.values()
        ):
            raise ValueError("Alert delivery counters must be non-negative integers.")

    def report_batch(
        self,
        *,
        claimed: int,
        delivered: int,
        retry_scheduled: int,
        terminal_failed: int,
        lease_lost: int,
    ) -> None:
        counts = {
            "claimed": claimed,
            "delivered": delivered,
            "retry_scheduled": retry_scheduled,
            "terminal_failed": terminal_failed,
            "lease_lost": lease_lost,
        }
        self._validate_counts(**counts)
        degraded_flags = (
            retry_scheduled > 0,
            terminal_failed > 0,
            lease_lost > 0,
        )
        if any(degraded_flags):
            signature = ("degraded", *degraded_flags)
            if signature != self._last_state:
                self._record_incident(
                    fingerprint="alert_delivery_degraded", category="alert_delivery",
                    severity="critical" if terminal_failed > 0 or lease_lost > 0 else "warning",
                    summary_code="delivery_attention",
                )
                self._logger.warning(json.dumps({
                    "event": "alert_delivery_attention",
                    "state": "degraded",
                    **counts,
                }, separators=(",", ":"), sort_keys=True))
            self._last_state = signature
            return

        if self._last_state is not None:
            self._resolve_incidents("alert_delivery")
            self._logger.info(json.dumps({
                "event": "alert_delivery_recovered",
                "state": "healthy",
            }, separators=(",", ":"), sort_keys=True))
            self._last_state = None

    def report_error(self, error: Exception) -> None:
        if not isinstance(error, Exception):
            raise TypeError("error must be an Exception.")
        raw_name = type(error).__name__
        error_code = "".join(
            char for char in raw_name
            if char.isascii() and (char.isalnum() or char == "_")
        )[:64] or "UnknownError"
        signature = ("worker_error", error_code)
        if signature == self._last_state:
            return
        self._record_incident(
            fingerprint=f"alert_delivery_worker:{error_code.lower()}", category="alert_delivery",
            severity="critical", summary_code="worker_error",
        )
        self._logger.error(json.dumps({
            "event": "alert_delivery_worker_error",
            "state": "error",
            "error_code": error_code,
        }, separators=(",", ":"), sort_keys=True))
        self._last_state = signature

    def _record_incident(self, **fields: str) -> None:
        if self._incident_store is None:
            return
        try:
            self._incident_store.record_incident(**fields)
        except Exception as exc:
            self._logger.error(json.dumps({
                "event": "incident_journal_write_failed",
                "error_code": type(exc).__name__[:64],
            }, separators=(",", ":"), sort_keys=True))

    def _resolve_incidents(self, category: str) -> None:
        if self._incident_store is None:
            return
        try:
            self._incident_store.resolve_category(category)
        except Exception as exc:
            self._logger.error(json.dumps({
                "event": "incident_journal_recovery_update_failed",
                "error_code": type(exc).__name__[:64],
            }, separators=(",", ":"), sort_keys=True))
