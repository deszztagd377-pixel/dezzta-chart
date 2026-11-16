"""Owner-scoped FCM fan-out for durable price-alert trigger events.

This adapter intentionally processes at most the device-store quota (10)
recipients for one event. A retry may resend to devices already reached, so
Android clients must deduplicate using event_id.
"""
from __future__ import annotations

from app.alert_device_store import SQLiteAlertDeviceStore
from app.alert_store import PriceAlertTriggerEvent
from app.fcm_sender import FCMDeliveryError, FirebaseCloudMessagingSender


def build_alert_event_sender(
    device_store: SQLiteAlertDeviceStore,
    fcm_sender: FirebaseCloudMessagingSender,
):
    """Build the synchronous sender callback expected by alert_delivery.

    Permanent FCM token failures revoke only the affected owner's installation.
    Retryable failures abort the event batch so the durable outbox can retry it.
    """
    if not isinstance(device_store, SQLiteAlertDeviceStore):
        raise TypeError("device_store must be a SQLiteAlertDeviceStore.")
    if not isinstance(fcm_sender, FirebaseCloudMessagingSender):
        raise TypeError("fcm_sender must be a FirebaseCloudMessagingSender.")

    def send_event(event: PriceAlertTriggerEvent) -> None:
        devices = device_store.active_tokens_for_delivery(
            owner_id=event.owner_id,
            limit=10,
        )
        for device in devices:
            try:
                fcm_sender.send_price_alert(token=device.token, event=event)
            except FCMDeliveryError as exc:
                if exc.token_invalid:
                    # Only explicit registration-token invalidation codes may
                    # revoke a device. Other permanent errors may be payload or
                    # project configuration faults, not bad installation tokens.
                    device_store.revoke(
                        owner_id=event.owner_id,
                        installation_id=device.installation_id,
                    )
                    continue
                raise
        return None

    return send_event
