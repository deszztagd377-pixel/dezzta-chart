from types import SimpleNamespace

import pytest

from app.alert_device_store import SQLiteAlertDeviceStore
from app.alert_fcm_delivery import build_alert_event_sender
from app.alert_device_store import SQLiteAlertDeviceStore
from app.fcm_sender import FCMDeliveryError, FCMDeliveryResult, FirebaseCloudMessagingSender


@pytest.fixture
def device_store(tmp_path):
    return SQLiteAlertDeviceStore(
        str(tmp_path / "alerts.sqlite3"),
        encryption_key=b"K" * 32,
    )


def event(**overrides):
    values = {
        "event_id": "event-1",
        "zone_id": "zone-1",
        "owner_id": "account-a",
        "canonical_instrument_id": "instrument-1",
        "trigger_price": "100.25",
        "provider_event_id": "provider-event-1",
        "source_timestamp_ns": 1_700_000_000_000_000_000,
        "delivery_status": "pending",
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def make_fcm(send):
    return FirebaseCloudMessagingSender(
        "test-project",
        send_callable=send,
        message_factory=lambda data, token: (data, token),
        firebase_app=object(),
    )


def test_fanout_sends_only_to_active_devices_owned_by_event_account(device_store):
    device_store.register(owner_id="account-a", installation_id="a1", fcm_token="token-a1")
    device_store.register(owner_id="account-a", installation_id="a2", fcm_token="token-a2")
    device_store.register(owner_id="account-b", installation_id="b1", fcm_token="token-b1")
    device_store.revoke(owner_id="account-a", installation_id="a2")
    sent = []

    def send(message, *, app):
        sent.append(message[1])
        return f"message-{len(sent)}"

    sender = build_alert_event_sender(device_store, make_fcm(send))
    assert sender(event()) is None
    assert sent == ["token-a1"]


def test_fanout_revokes_only_permanently_invalid_installation(device_store):
    device_store.register(owner_id="account-a", installation_id="bad", fcm_token="bad-token")
    device_store.register(owner_id="account-a", installation_id="good", fcm_token="good-token")

    def send(message, *, app):
        if message[1] == "bad-token":
            raise FCMDeliveryError("unregistered", retryable=False)
        return "message-good"

    sender = build_alert_event_sender(device_store, make_fcm(send))
    assert sender(event()) is None
    assert device_store.token_for_delivery(owner_id="account-a", installation_id="bad") is None
    assert device_store.token_for_delivery(owner_id="account-a", installation_id="good") == "good-token"


def test_fanout_propagates_retryable_error_for_outbox_retry(device_store):
    device_store.register(owner_id="account-a", installation_id="phone", fcm_token="token")

    def send(message, *, app):
        raise FCMDeliveryError("unavailable", retryable=True)

    sender = build_alert_event_sender(device_store, make_fcm(send))
    with pytest.raises(FCMDeliveryError) as raised:
        sender(event())
    assert raised.value.retryable is True
    assert device_store.token_for_delivery(owner_id="account-a", installation_id="phone") == "token"


def test_fanout_with_no_registered_devices_completes_without_leaking_recipients(device_store):
    sender = build_alert_event_sender(
        device_store,
        make_fcm(lambda message, *, app: "unused"),
    )
    assert sender(event()) is None
