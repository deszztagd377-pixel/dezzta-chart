"""Firebase Cloud Messaging adapter for durable price-alert events.

This module is deliberately not started by the API lifespan yet. Production
initialization uses Application Default Credentials (ADC); no service-account
key or credential value is accepted from application configuration.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


_RETRYABLE_CODES = frozenset({
    "internal",
    "unavailable",
    "deadline-exceeded",
    "quota-exceeded",
    "resource-exhausted",
    "server-unavailable",
    "unknown",
})
_PERMANENT_CODES = frozenset({
    "invalid-argument",
    "registration-token-not-registered",
    "unregistered",
    "sender-id-mismatch",
    "third-party-auth-error",
})


class FCMDeliveryError(RuntimeError):
    """Sanitized FCM failure classification; never retains provider payloads."""

    def __init__(self, code: str, *, retryable: bool) -> None:
        self.code = code
        self.retryable = retryable
        super().__init__(f"FCM delivery failed ({code}).")


@dataclass(frozen=True, slots=True)
class FCMDeliveryResult:
    message_id: str


class FirebaseCloudMessagingSender:
    """Send one data-only alert to one registered installation.

    The event_id is included in the payload so Android clients can deduplicate
    at-least-once deliveries. FCM itself does not provide exactly-once delivery.
    """

    def __init__(
        self,
        project_id: str,
        *,
        send_callable: Callable[..., str] | None = None,
        message_factory: Callable[[dict[str, str], str], Any] | None = None,
        firebase_app: Any = None,
    ) -> None:
        if not isinstance(project_id, str) or not project_id.strip():
            raise ValueError("project_id is required.")
        self._project_id = project_id.strip()
        self._send_callable = send_callable
        self._message_factory = message_factory
        self._firebase_app = firebase_app

    @classmethod
    def from_application_credentials(cls, project_id: str) -> "FirebaseCloudMessagingSender":
        """Create/reuse a named Firebase Admin app using runtime ADC."""
        if not isinstance(project_id, str) or not project_id.strip():
            raise ValueError("project_id is required.")
        try:
            import firebase_admin
            from firebase_admin import credentials, messaging
        except ImportError as exc:
            raise RuntimeError("Firebase Admin SDK is unavailable.") from exc

        normalized_project = project_id.strip()
        try:
            try:
                app = firebase_admin.get_app(normalized_project)
            except ValueError:
                app = firebase_admin.initialize_app(
                    credential=credentials.ApplicationDefault(),
                    options={"projectId": normalized_project},
                    name=normalized_project,
                )
        except Exception as exc:
            # Do not expose ADC paths, credential contents, or SDK internals.
            raise RuntimeError("Firebase Admin could not initialize from runtime credentials.") from exc

        def build_message(data: dict[str, str], token: str) -> Any:
            return messaging.Message(
                data=data,
                token=token,
                android=messaging.AndroidConfig(priority="high"),
                apns=messaging.APNSConfig(headers={"apns-priority": "10"}),
            )

        return cls(
            normalized_project,
            send_callable=messaging.send,
            message_factory=build_message,
            firebase_app=app,
        )

    @staticmethod
    def _error_code(error: Exception) -> str:
        raw_code = getattr(error, "code", None)
        if callable(raw_code):
            try:
                raw_code = raw_code()
            except Exception:
                raw_code = None
        if not isinstance(raw_code, str) or not raw_code:
            raw_code = error.__class__.__name__
        normalized = raw_code.rsplit("/", 1)[-1].replace("_", "-").lower()
        return normalized[:64] or "unknown"

    def send_price_alert(self, *, token: str, event: Any) -> FCMDeliveryResult:
        if not isinstance(token, str) or not token.strip() or len(token) > 4096:
            raise ValueError("A valid FCM registration token is required.")
        required = ("event_id", "zone_id", "canonical_instrument_id", "trigger_price", "source_timestamp_ns")
        values = {name: getattr(event, name, None) for name in required}
        if any(value is None for value in values.values()):
            raise ValueError("The price-alert event is incomplete.")
        data = {
            "type": "price_alert",
            "event_id": str(values["event_id"]),
            "zone_id": str(values["zone_id"]),
            "instrument_id": str(values["canonical_instrument_id"]),
            "trigger_price": str(values["trigger_price"]),
            "source_timestamp_ns": str(values["source_timestamp_ns"]),
        }
        if any(not value or len(value) > 256 for value in data.values()):
            raise ValueError("The price-alert event contains invalid fields.")
        if self._send_callable is None or self._message_factory is None:
            raise RuntimeError("Firebase Cloud Messaging sender is not initialized.")
        message = self._message_factory(data, token.strip())
        try:
            message_id = self._send_callable(message, app=self._firebase_app)
        except Exception as exc:
            code = self._error_code(exc)
            if code in _PERMANENT_CODES:
                retryable = False
            elif code in _RETRYABLE_CODES:
                retryable = True
            else:
                # Unknown provider errors are retried by the bounded outbox
                # policy rather than silently dropping a potentially valid event.
                retryable = True
                code = "unknown"
            raise FCMDeliveryError(code, retryable=retryable) from None
        if not isinstance(message_id, str) or not message_id.strip():
            raise FCMDeliveryError("invalid-provider-response", retryable=True)
        return FCMDeliveryResult(message_id=message_id)
