"""Hard-deadline process isolation for Firebase alert fan-out.

A provider SDK call may block inside synchronous code and cannot be reliably
cancelled by asyncio. Run one event's bounded (at most 10-recipient) fan-out in
a disposable child process. If the event deadline expires, terminate the child;
the durable outbox retries with the same event_id (at-least-once semantics).
"""
from __future__ import annotations

import multiprocessing
import re
from types import SimpleNamespace
from typing import Any, Callable

from app.alert_device_store import SQLiteAlertDeviceStore
from app.alert_fcm_delivery import build_alert_event_sender
from app.fcm_sender import FCMDeliveryError, FirebaseCloudMessagingSender

ALERT_FCM_EVENT_TIMEOUT_SECONDS = 60
ALERT_FCM_PROCESS_EXIT_GRACE_SECONDS = 2
_ALLOWED_ERROR_CODE = re.compile(r"^[a-z0-9-]{1,64}$")


def _deliver_event_child(
    send_connection: Any,
    database_path: str,
    encryption_key: bytes,
    project_id: str,
    event_payload: dict[str, object],
) -> None:
    """Initialize ADC and deliver one event entirely inside the child process."""
    try:
        device_store = SQLiteAlertDeviceStore(
            database_path,
            encryption_key=encryption_key,
        )
        fcm_sender = FirebaseCloudMessagingSender.from_application_credentials(
            project_id
        )
        event_sender = build_alert_event_sender(device_store, fcm_sender)
        event_sender(SimpleNamespace(**event_payload))
        result = {"ok": True}
    except FCMDeliveryError as exc:
        result = {
            "ok": False,
            "code": exc.code,
            "retryable": exc.retryable,
            "token_invalid": exc.token_invalid,
        }
    except Exception:
        # Never return provider payloads, tokens, credential paths or tracebacks.
        result = {
            "ok": False,
            "code": "worker-process-failed",
            "retryable": True,
            "token_invalid": False,
        }
    try:
        send_connection.send(result)
    except (BrokenPipeError, EOFError, OSError):
        pass
    finally:
        send_connection.close()


def _stop_process(process: Any) -> None:
    """Bound child cleanup; escalate terminate to kill if needed."""
    if not process.is_alive():
        process.join(timeout=0)
        return
    process.terminate()
    process.join(timeout=ALERT_FCM_PROCESS_EXIT_GRACE_SECONDS)
    if process.is_alive():
        kill = getattr(process, "kill", None)
        if callable(kill):
            kill()
        process.join(timeout=ALERT_FCM_PROCESS_EXIT_GRACE_SECONDS)


def _run_bounded_process(
    target: Callable[..., None],
    args: tuple[object, ...],
    *,
    timeout_seconds: float,
) -> dict[str, object]:
    """Run a spawn-isolated target and enforce a parent-observed deadline."""
    if (
        not isinstance(timeout_seconds, (int, float))
        or isinstance(timeout_seconds, bool)
        or not 0 < timeout_seconds <= 120
    ):
        raise ValueError("timeout_seconds must be greater than 0 and at most 120.")
    context = multiprocessing.get_context("spawn")
    receive_connection, send_connection = context.Pipe(duplex=False)
    process = context.Process(
        target=target,
        args=(send_connection, *args),
        name="dezzta-fcm-event",
        daemon=True,
    )
    started = False
    try:
        process.start()
        started = True
        send_connection.close()
        if not receive_connection.poll(timeout_seconds):
            _stop_process(process)
            raise TimeoutError("FCM event delivery exceeded its deadline.")
        try:
            result = receive_connection.recv()
        except (EOFError, OSError) as exc:
            raise RuntimeError("FCM child exited without a result.") from exc
        process.join(timeout=ALERT_FCM_PROCESS_EXIT_GRACE_SECONDS)
        if process.is_alive():
            _stop_process(process)
            raise RuntimeError("FCM child did not exit after returning its result.")
        if process.exitcode != 0:
            raise RuntimeError("FCM child exited unsuccessfully.")
        if not isinstance(result, dict):
            raise RuntimeError("FCM child returned an invalid result.")
        return result
    except Exception:
        if started and process.is_alive():
            _stop_process(process)
        raise
    finally:
        receive_connection.close()
        try:
            send_connection.close()
        except OSError:
            pass
        if started and not process.is_alive():
            process.close()


def build_isolated_alert_event_sender(
    *,
    database_path: str,
    encryption_key: bytes,
    project_id: str,
    timeout_seconds: int = ALERT_FCM_EVENT_TIMEOUT_SECONDS,
    process_runner: Callable[..., dict[str, object]] = _run_bounded_process,
) -> Callable[[Any], None]:
    """Build an event sender with a strict total fan-out deadline.

    Only the encrypted SQLite path, owner-injected key and event metadata enter
    the child. FCM registration tokens are read/decrypted inside that process
    and never cross the IPC pipe. A timeout may follow partial provider
    acceptance; the stable event_id is therefore the recipient deduplication key.
    """
    if not isinstance(database_path, str) or not database_path.strip():
        raise ValueError("database_path is required.")
    if not isinstance(encryption_key, bytes) or len(encryption_key) != 32:
        raise ValueError("encryption_key must contain exactly 32 bytes.")
    if not isinstance(project_id, str) or not project_id.strip():
        raise ValueError("project_id is required.")
    if not callable(process_runner):
        raise ValueError("process_runner must be callable.")

    def send_event(event: Any) -> None:
        required = (
            "event_id",
            "zone_id",
            "owner_id",
            "canonical_instrument_id",
            "trigger_price",
            "source_timestamp_ns",
        )
        payload = {name: getattr(event, name, None) for name in required}
        if any(value is None for value in payload.values()):
            raise ValueError("The price-alert event is incomplete.")
        try:
            result = process_runner(
                _deliver_event_child,
                (database_path, encryption_key, project_id.strip(), payload),
                timeout_seconds=timeout_seconds,
            )
        except TimeoutError:
            raise FCMDeliveryError("delivery-timeout", retryable=True) from None
        except Exception:
            raise FCMDeliveryError("worker-process-failed", retryable=True) from None
        if result.get("ok") is True:
            return None
        code = result.get("code")
        if not isinstance(code, str) or not _ALLOWED_ERROR_CODE.fullmatch(code):
            code = "worker-process-failed"
        retryable = result.get("retryable")
        token_invalid = result.get("token_invalid")
        if not isinstance(retryable, bool) or not isinstance(token_invalid, bool):
            raise FCMDeliveryError("worker-process-failed", retryable=True)
        raise FCMDeliveryError(
            code,
            retryable=retryable,
            token_invalid=token_invalid,
        )

    return send_event
