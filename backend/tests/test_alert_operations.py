import json
import logging

import pytest

from app.alert_operations import LocalAlertReporter


def test_local_reporter_emits_one_sanitized_attention_alert_per_state(caplog):
    logger = logging.getLogger("test.dezzta.alert_operations.batch")
    reporter = LocalAlertReporter(logger)

    with caplog.at_level(logging.WARNING, logger=logger.name):
        reporter.report_batch(
            claimed=1, delivered=0, retry_scheduled=1,
            terminal_failed=0, lease_lost=0,
        )
        reporter.report_batch(
            claimed=3, delivered=0, retry_scheduled=2,
            terminal_failed=0, lease_lost=0,
        )
        reporter.report_batch(
            claimed=1, delivered=0, retry_scheduled=0,
            terminal_failed=1, lease_lost=0,
        )

    records = [json.loads(record.message) for record in caplog.records]
    assert len(records) == 2
    assert records[0]["event"] == "alert_delivery_attention"
    assert records[0]["retry_scheduled"] == 1
    assert records[1]["terminal_failed"] == 1
    serialized = " ".join(record.message for record in caplog.records)
    assert "owner_id" not in serialized
    assert "registration_token" not in serialized
    assert "provider_payload" not in serialized


def test_local_reporter_emits_recovery_only_after_degraded_state(caplog):
    logger = logging.getLogger("test.dezzta.alert_operations.recovery")
    reporter = LocalAlertReporter(logger)

    with caplog.at_level(logging.INFO, logger=logger.name):
        reporter.report_batch(
            claimed=0, delivered=0, retry_scheduled=0,
            terminal_failed=0, lease_lost=0,
        )
        assert caplog.records == []
        reporter.report_batch(
            claimed=1, delivered=0, retry_scheduled=0,
            terminal_failed=1, lease_lost=0,
        )
        reporter.report_batch(
            claimed=0, delivered=0, retry_scheduled=0,
            terminal_failed=0, lease_lost=0,
        )

    records = [json.loads(record.message) for record in caplog.records]
    assert [record["event"] for record in records] == [
        "alert_delivery_attention", "alert_delivery_recovered"
    ]


def test_local_reporter_sanitizes_and_deduplicates_worker_errors(caplog):
    logger = logging.getLogger("test.dezzta.alert_operations.errors")
    reporter = LocalAlertReporter(logger)
    error = RuntimeError("secret token and provider response must never be logged")

    with caplog.at_level(logging.ERROR, logger=logger.name):
        reporter.report_error(error)
        reporter.report_error(error)

    assert len(caplog.records) == 1
    record = json.loads(caplog.records[0].message)
    assert record == {
        "error_code": "RuntimeError",
        "event": "alert_delivery_worker_error",
        "state": "error",
    }
    assert "secret token" not in caplog.records[0].message


@pytest.mark.parametrize("value", [-1, True, 1.5, "1"])
def test_local_reporter_rejects_invalid_counters(value):
    reporter = LocalAlertReporter(logging.getLogger("test.dezzta.alert_operations.invalid"))
    with pytest.raises(ValueError):
        reporter.report_batch(
            claimed=value, delivered=0, retry_scheduled=0,
            terminal_failed=0, lease_lost=0,
        )
