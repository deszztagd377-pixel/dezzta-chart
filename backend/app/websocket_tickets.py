"""Short-lived single-use WebSocket tickets; memory store is non-production only."""
from __future__ import annotations
import asyncio
import hashlib
import secrets
import time

WEBSOCKET_TICKET_TTL_SECONDS = 90
WEBSOCKET_TICKET_PURPOSE = "market-data"


class InMemoryWebSocketTicketStore:
    """Single-process development/test store. Production must use Redis."""
    def __init__(self, *, ttl_seconds: int = WEBSOCKET_TICKET_TTL_SECONDS) -> None:
        if not isinstance(ttl_seconds, int) or isinstance(ttl_seconds, bool) or not 30 <= ttl_seconds <= 120:
            raise ValueError("WebSocket ticket TTL must be between 30 and 120 seconds.")
        self.ttl_seconds = ttl_seconds
        self._tickets: dict[str, tuple[str, str, float]] = {}
        self._lock = asyncio.Lock()

    @staticmethod
    def _digest(ticket: str) -> str:
        return hashlib.sha256(ticket.encode("ascii")).hexdigest()

    async def issue_websocket_ticket(self, account_subject: str) -> str:
        if not isinstance(account_subject, str) or not account_subject.strip() or len(account_subject) > 128:
            raise ValueError("A verified account subject is required.")
        async with self._lock:
            now = time.monotonic()
            self._tickets = {k: v for k, v in self._tickets.items() if v[2] > now}
            if len(self._tickets) >= 4096:
                raise RuntimeError("The development WebSocket ticket store is at capacity.")
            for _ in range(3):
                ticket = secrets.token_urlsafe(32)
                digest = self._digest(ticket)
                if digest not in self._tickets:
                    self._tickets[digest] = (account_subject, WEBSOCKET_TICKET_PURPOSE, now + self.ttl_seconds)
                    return ticket
        raise RuntimeError("A unique WebSocket ticket could not be created.")

    async def consume_websocket_ticket(self, ticket: str, *, purpose: str = WEBSOCKET_TICKET_PURPOSE) -> str | None:
        if not isinstance(ticket, str) or not 40 <= len(ticket) <= 128 or not ticket.isascii():
            return None
        digest = self._digest(ticket)
        async with self._lock:
            stored = self._tickets.pop(digest, None)
            if stored is None:
                return None
            subject, stored_purpose, expires_at = stored
            if expires_at <= time.monotonic() or stored_purpose != purpose:
                return None
            return subject
