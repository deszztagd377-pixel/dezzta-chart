import time
from types import SimpleNamespace

import pytest

from app.alert_fcm_process import (
    ALERT_FCM_EVENT_TIMEOUT_SECONDS,
    _run_bounded_process,
    build_isolated_alert_event_sender,
)
from app.fcm_sender import FCMDeliveryError


def _child_send_value(connection, value):
    connection.send(value)
    connection.close()


def _child_wait_forever(connection):
    time.sleep(5)
    connection.send({"ok": True})
    connection.close()


def _event(**overrides):
    values = {
        "event_id": "stable-event-id",
        "zone_id": "zone-1",
        "owner_id": "account-a",
        "canonical_instrument_id": "instrument-1",
        "trigger_price": "100.25",
        "source_timestamp_ns": 1_700_000_000_000_000_000,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def test_spawn_child_returns_sanitized_result():
    result = _run_bounded_process(
        _child_send_value,
        ({"ok": True, "count": 3},),
        timeout_seconds=10,
    )
    assert result == {"ok": True, "count": 3}


def test_spawn_child_is_terminated_at_deadline():
    started = time.monotonic()
    with pytest.raises(TimeoutError, match="exceeded its deadline"):
        _run_bounded_process(
            _child_wait_forever,
            (),
            timeout_seconds=0.1,
        )
    assert time.monotonic() - started < 3


def test_isolated_sender_passes_only_event_metadata_to_child():
    captured = {}

    def runner(target, args, *, timeout_seconds):
        captured.update({"target": target, "args": args, "timeout": timeout_seconds})
        return {"ok": True}

    sender = build_isolated_alert_event_sender(
        database_path="/tmp/alerts.sqlite3",
        encryption_key=b"K" * 32,
        project_id="test-project",
        process_runner=runner,
    )
    assert sender(_event()) is None
    assert captured["target"].__name__ == "_deliver_event_child"
    assert captured["args"][0] == "/tmp/alerts.sqlite3"
    assert captured["args"][1] == b"K" * 32
    assert captured["args"][2] == "test-project"
    assert captured["args"][3]["event_id"] == "stable-event-id"
    assert "token" not in captured["args"][3]
    assert captured["timeout"] == ALERT_FCM_EVENT_TIMEOUT_SECONDS


def test_isolated_sender_maps_timeout_to_retryable_outbox_error():
    def runner(target, args, *, timeout_seconds):
        raise TimeoutError("provider internals must not leak")

    sender = build_isolated_alert_event_sender(
        database_path="/tmp/alerts.sqlite3",
        encryption_key=b"K" * 32,
        project_id="test-project",
        process_runner=runner,
    )
    with pytest.raises(FCMDeliveryError) as raised:
        sender(_event())
    assert raised.value.code == "delivery-timeout"
    assert raised.value.retryable is True
    assert "provider internals" not in str(raised.value)


def test_isolated_sender_preserves_sanitized_provider_classification():
    def runner(target, args, *, timeout_seconds):
        return {
            "ok": False,
            "code": "unregistered",
            "retryable": False,
            "token_invalid": True,
        }

    sender = build_isolated_alert_event_sender(
        database_path="/tmp/alerts.sqlite3",
        encryption_key=b"K" * 32,
        project_id="test-project",
        process_runner=runner,
    )
    with pytest.raises(FCMDeliveryError) as raised:
        sender(_event())
    assert raised.value.code == "unregistered"
    assert raised.value.retryable is False
    assert raised.value.token_invalid is True


def test_isolated_sender_rejects_incomplete_event_before_starting_child():
    started = False

    def runner(target, args, *, timeout_seconds):
        nonlocal started
        started = True
        return {"ok": True}

    sender = build_isolated_alert_event_sender(
        database_path="/tmp/alerts.sqlite3",
        encryption_key=b"K" * 32,
        project_id="test-project",
        process_runner=runner,
    )
    with pytest.raises(ValueError, match="incomplete"):
        sender(_event(event_id=None))
    assert started is False


def test_spawn_startup_time_consumes_event_deadline(monkeypatch):
    import app.alert_fcm_process as isolated

    clock = {"now": 10.0}
    observed = {"terminated": False, "closed": False}

    class FakeConnection:
        def poll(self, timeout):
            observed["poll_timeout"] = timeout
            return False

        def close(self):
            observed["connection_closed"] = True

    class FakeProcess:
        exitcode = -15

        def start(self):
            # Simulate spawn startup consuming more than the 100 ms budget.
            clock["now"] += 0.2
            self.alive = True

        def is_alive(self):
            return self.alive

        def terminate(self):
            observed["terminated"] = True
            self.alive = False

        def join(self, timeout=0):
            observed.setdefault("join_timeouts", []).append(timeout)

        def close(self):
            observed["closed"] = True

    class FakeContext:
        def Pipe(self, duplex=False):
            return FakeConnection(), FakeConnection()

        def Process(self, **kwargs):
            return FakeProcess()

    monkeypatch.setattr(isolated.multiprocessing, "get_context", lambda method: FakeContext())
    monkeypatch.setattr(isolated.time, "monotonic", lambda: clock["now"])

    with pytest.raises(TimeoutError, match="exceeded its deadline"):
        isolated._run_bounded_process(
            _child_send_value,
            ({"ok": True},),
            timeout_seconds=0.1,
        )

    assert observed["terminated"] is True
    assert observed["closed"] is True
    assert "poll_timeout" not in observed
