from types import SimpleNamespace

import pytest

from app.fcm_sender import (
    FCMDeliveryError,
    FirebaseCloudMessagingSender,
)


def make_event(**overrides):
    values = {
        "event_id": "event-123",
        "zone_id": "zone-123",
        "canonical_instrument_id": "instrument-123",
        "trigger_price": "123.4500",
        "source_timestamp_ns": 1_700_000_000_000_000_000,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def make_sender(send_callable):
    captured = {}

    def message_factory(data, token):
        captured["data"] = data
        captured["token"] = token
        return {"data": data, "token": token}

    sender = FirebaseCloudMessagingSender(
        "dezzta-test",
        send_callable=send_callable,
        message_factory=message_factory,
        firebase_app=object(),
    )
    return sender, captured


def test_sender_sends_data_only_event_with_stable_deduplication_id():
    def send(message, *, app):
        assert app is not None
        return "projects/dezzta-test/messages/1"

    sender, captured = make_sender(send)
    result = sender.send_price_alert(token="fcm-token", event=make_event())

    assert result.message_id.endswith("/1")
    assert captured["token"] == "fcm-token"
    assert captured["data"] == {
        "type": "price_alert",
        "event_id": "event-123",
        "zone_id": "zone-123",
        "instrument_id": "instrument-123",
        "trigger_price": "123.4500",
        "source_timestamp_ns": "1700000000000000000",
    }


@pytest.mark.parametrize("token", ["", " ", "bad token " + "x" * 4096, None])
def test_sender_rejects_invalid_registration_token(token):
    sender, _ = make_sender(lambda message, *, app: "message-id")
    with pytest.raises(ValueError, match="registration token"):
        sender.send_price_alert(token=token, event=make_event())


def test_sender_rejects_incomplete_event():
    sender, _ = make_sender(lambda message, *, app: "message-id")
    with pytest.raises(ValueError, match="incomplete"):
        sender.send_price_alert(
            token="fcm-token",
            event=make_event(event_id=None),
        )


@pytest.mark.parametrize(
    ("provider_code", "retryable", "expected_code"),
    [
        ("UNREGISTERED", False, "unregistered"),
        ("SENDER_ID_MISMATCH", False, "sender-id-mismatch"),
        ("INVALID_ARGUMENT", False, "invalid-argument"),
        ("UNAVAILABLE", True, "unavailable"),
        ("QUOTA_EXCEEDED", True, "quota-exceeded"),
        ("INTERNAL", True, "internal"),
        ("SOME_NEW_PROVIDER_ERROR", True, "unknown"),
    ],
)
def test_sender_classifies_provider_errors_without_leaking_details(
    provider_code, retryable, expected_code
):
    class ProviderError(Exception):
        code = provider_code

        def __str__(self):
            return "sensitive provider response and token material"

    def fail(message, *, app):
        raise ProviderError()

    sender, _ = make_sender(fail)
    with pytest.raises(FCMDeliveryError) as raised:
        sender.send_price_alert(token="fcm-token", event=make_event())

    assert raised.value.retryable is retryable
    assert raised.value.code == expected_code
    assert "sensitive" not in str(raised.value)


def test_sender_rejects_empty_provider_message_id():
    sender, _ = make_sender(lambda message, *, app: " ")
    with pytest.raises(FCMDeliveryError) as raised:
        sender.send_price_alert(token="fcm-token", event=make_event())
    assert raised.value.retryable is True
    assert raised.value.code == "invalid-provider-response"


def test_sender_requires_explicit_initialization():
    sender = FirebaseCloudMessagingSender("dezzta-test")
    with pytest.raises(RuntimeError, match="not initialized"):
        sender.send_price_alert(token="fcm-token", event=make_event())
