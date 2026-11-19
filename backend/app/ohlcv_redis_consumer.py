"""Per-gateway Redis Streams consumer with durable apply-before-ACK semantics.

Each replica owns an independent Redis consumer group. The local SQLite
replica checkpoint is authoritative for applied progress; Redis pending entries
are reclaimed and replayed idempotently after process failure.
"""
from __future__ import annotations

import json
import hashlib
from typing import Any, Callable

from app.ohlcv_store import SQLiteOhlcvReplicaStore
from app.ohlcv_redis_publisher import (
    RedisOhlcvStreamAppender,
    _redis_text,
)


class ReplicaResnapshotRequired(RuntimeError):
    """A stream gap, expired history, or deleted pending entry requires a snapshot."""


class RedisOhlcvReplicaConsumer:
    """Consume one source stream into one durable gateway replica.

    The consumer group name is derived from the stable local replica identity,
    so every gateway receives its own broadcast copy. One sequential consumer
    should be active per replica group. A new consumer process can reclaim
    abandoned pending messages using XAUTOCLAIM.
    """

    def __init__(
        self,
        redis_client: Any,
        replica_store: SQLiteOhlcvReplicaStore,
        *,
        stream_key: str,
        consumer_name: str,
        pending_idle_ms: int = 30_000,
        batch_size: int = 100,
        block_ms: int | None = None,
        on_event_applied: Callable[[dict[str, Any]], None] | None = None,
    ) -> None:
        if redis_client is None:
            raise ValueError("redis_client is required.")
        if not isinstance(replica_store, SQLiteOhlcvReplicaStore):
            raise TypeError("replica_store must be a SQLiteOhlcvReplicaStore.")
        if not isinstance(stream_key, str) or not stream_key.strip() or len(stream_key) > 256:
            raise ValueError("stream_key must be a non-empty string of at most 256 characters.")
        if not isinstance(consumer_name, str) or not consumer_name.strip() or len(consumer_name) > 128:
            raise ValueError("consumer_name must be a non-empty string of at most 128 characters.")
        if type(pending_idle_ms) is not int or not 0 <= pending_idle_ms <= 86_400_000:
            raise ValueError("pending_idle_ms must be between 0 and 86400000.")
        if type(batch_size) is not int or not 1 <= batch_size <= 1_000:
            raise ValueError("batch_size must be between 1 and 1000.")
        if block_ms is not None and (
            type(block_ms) is not int or not 1 <= block_ms <= 30_000
        ):
            raise ValueError("block_ms must be None or between 1 and 30000.")

        checkpoint = replica_store.checkpoint()
        if checkpoint is None:
            raise RuntimeError("Install a verified global snapshot before creating a replica consumer.")
        self.source_id = str(checkpoint["source_id"])
        self._replica_id = replica_store.replica_id()
        self._source_suffix = hashlib.sha256(self.source_id.encode("utf-8")).hexdigest()[:12]
        self._snapshot_generation = str(checkpoint["snapshot_generation"])
        if not self._snapshot_generation:
            raise RuntimeError("Replica snapshot generation is missing.")
        self.group_name = self._group_name_for_generation(self._snapshot_generation)
        self.redis = redis_client
        self.replica_store = replica_store
        self.stream_key = stream_key
        self.consumer_name = consumer_name
        self.pending_idle_ms = pending_idle_ms
        self.batch_size = batch_size
        if on_event_applied is not None and not callable(on_event_applied):
            raise TypeError("on_event_applied must be callable when provided.")
        self.block_ms = block_ms
        self.on_event_applied = on_event_applied
        self._pending_scan_id = "0-0"

    def _group_name_for_generation(self, generation: str) -> str:
        if not isinstance(generation, str) or not generation:
            raise RuntimeError("Replica snapshot generation is missing.")
        generation_suffix = hashlib.sha256(generation.encode("utf-8")).hexdigest()[:12]
        return (
            f"dezzta:ohlcv:gateway:{self._replica_id}:"
            f"{self._source_suffix}:{generation_suffix}"
        )

    def _refresh_group_generation(self, checkpoint: dict[str, Any]) -> None:
        if str(checkpoint.get("source_id")) != self.source_id:
            raise RuntimeError("Replica source checkpoint is missing or changed.")
        generation = checkpoint.get("snapshot_generation")
        if not isinstance(generation, str) or not generation:
            raise RuntimeError("Replica snapshot generation is missing.")
        if generation != self._snapshot_generation:
            self._snapshot_generation = generation
            self.group_name = self._group_name_for_generation(generation)
            self._pending_scan_id = "0-0"

    def ensure_group(self) -> bool:
        """Create a fresh group at the installed snapshot cursor; preserve existing groups."""
        checkpoint = self.replica_store.checkpoint()
        if checkpoint is None:
            raise RuntimeError("Replica source checkpoint is missing or changed.")
        self._refresh_group_generation(checkpoint)
        start_id = f"{int(checkpoint['applied_cursor'])}-0"
        try:
            self.redis.xgroup_create(
                self.stream_key,
                self.group_name,
                id=start_id,
                mkstream=True,
            )
            return True
        except Exception as exc:
            if "BUSYGROUP" in str(exc).upper():
                return False
            raise

    def reset_group_after_snapshot(self) -> None:
        """Switch to a generation-scoped group after installing a new snapshot.

        The caller must quiesce this consumer before invoking the reset. A new
        group starts at the installed snapshot cursor, so obsolete pending
        deliveries remain isolated in the previous generation's group. No
        destructive XGROUP DESTROY permission is required by the runtime user.
        Old groups are intentionally retained for separately authorized cleanup.
        """
        checkpoint = self.replica_store.checkpoint()
        if checkpoint is None:
            raise RuntimeError("Installed snapshot does not match this consumer's source.")
        self._refresh_group_generation(checkpoint)
        self.ensure_group()

    def _decode_entry(self, stream_id: Any, raw_fields: Any) -> dict[str, Any]:
        entry_id = _redis_text(stream_id)
        if not isinstance(raw_fields, dict):
            raise ValueError("Redis OHLCV Stream entry fields must be an object.")
        fields = {
            _redis_text(key): _redis_text(value)
            for key, value in raw_fields.items()
        }
        if set(fields) != {"source_id", "event_id", "payload"}:
            raise ValueError("Redis OHLCV Stream entry fields do not match the protocol.")
        if fields["source_id"] != self.source_id:
            raise ValueError("Redis OHLCV Stream source identity does not match this replica.")
        try:
            event = json.loads(fields["payload"])
        except json.JSONDecodeError as exc:
            raise ValueError("Redis OHLCV Stream payload is not valid JSON.") from exc
        if not isinstance(event, dict):
            raise ValueError("Redis OHLCV Stream payload must be an event object.")
        if RedisOhlcvStreamAppender._canonical_payload(event) != fields["payload"]:
            raise ValueError("Redis OHLCV Stream payload is not canonical JSON.")
        if event.get("eventId") != fields["event_id"]:
            raise ValueError("Redis OHLCV Stream event ID does not match its payload.")
        cursor = event.get("cursor")
        if type(cursor) is not int or cursor < 1 or entry_id != f"{cursor}-0":
            raise ValueError("Redis Stream ID does not match the canonical event cursor.")
        return event

    def _apply_and_ack(self, entries: list[tuple[Any, Any]], *, reclaimed: bool) -> dict[str, Any]:
        applied = duplicate = stale = acknowledged = 0
        for stream_id, fields in entries:
            event = self._decode_entry(stream_id, fields)
            result = self.replica_store.apply_replica_event(
                event,
                source_id=self.source_id,
            )
            status = result.get("status")
            if status == "resnapshot_required":
                raise ReplicaResnapshotRequired(
                    "Replica must install a fresh global snapshot before acknowledging "
                    f"cursor {event['cursor']}: {result.get('reason', 'unknown')}."
                )
            if status not in {"applied", "duplicate", "stale"}:
                raise RuntimeError(f"Replica returned an unsupported apply status: {status!r}.")
            # The durable SQLite apply precedes this callback; fan-out must also
            # succeed before ACK. Invoke for duplicates too: a previous callback
            # may have failed between pipeline mutation and hub notification.
            # The hub's durable-cursor fence makes this retry idempotent.
            if status in {"applied", "duplicate"} and self.on_event_applied is not None:
                self.on_event_applied(event)
            # Durable local transaction and local fan-out precede Redis ACK.
            acknowledged += int(
                self.redis.xack(self.stream_key, self.group_name, stream_id) or 0
            )
            if status == "applied":
                applied += 1
            elif status == "duplicate":
                duplicate += 1
            else:
                stale += 1
        return {
            "status": "processed" if entries else "idle",
            "received": len(entries),
            "reclaimed": len(entries) if reclaimed else 0,
            "applied": applied,
            "duplicate": duplicate,
            "stale": stale,
            "acknowledged": acknowledged,
        }

    def consume_once(self) -> dict[str, Any]:
        """Reclaim pending first, then read new messages; process sequentially."""
        self.ensure_group()
        # Retry this consumer's own pending entries immediately. Waiting for
        # min_idle_ms here would allow a later new cursor to be read and fanned
        # out before a callback-failed earlier cursor owned by this same worker.
        own_pending_response = self.redis.xreadgroup(
            self.group_name,
            self.consumer_name,
            {self.stream_key: "0"},
            count=self.batch_size,
        )
        own_pending_entries: list[tuple[Any, Any]] = []
        for returned_stream, messages in own_pending_response or []:
            if _redis_text(returned_stream) != self.stream_key:
                raise ValueError("Redis returned an unexpected stream key for own pending entries.")
            own_pending_entries.extend(messages)
        if own_pending_entries:
            return self._apply_and_ack(own_pending_entries, reclaimed=True)

        reclaimed = self.redis.xautoclaim(
            self.stream_key,
            self.group_name,
            self.consumer_name,
            self.pending_idle_ms,
            start_id=self._pending_scan_id,
            count=self.batch_size,
        )
        if not isinstance(reclaimed, (tuple, list)) or len(reclaimed) < 2:
            raise RuntimeError("Redis XAUTOCLAIM returned an invalid response.")
        next_scan_id = _redis_text(reclaimed[0])
        pending_entries = reclaimed[1]
        deleted_ids = reclaimed[2] if len(reclaimed) > 2 else []
        if deleted_ids:
            raise ReplicaResnapshotRequired(
                "Redis reports pending stream entries were deleted; install a fresh snapshot."
            )
        self._pending_scan_id = next_scan_id
        if pending_entries:
            return self._apply_and_ack(list(pending_entries), reclaimed=True)
        if next_scan_id != "0-0":
            return {
                "status": "pending_scan",
                "received": 0,
                "reclaimed": 0,
                "applied": 0,
                "duplicate": 0,
                "stale": 0,
                "acknowledged": 0,
            }

        self._pending_scan_id = "0-0"
        kwargs: dict[str, Any] = {"count": self.batch_size}
        if self.block_ms is not None:
            kwargs["block"] = self.block_ms
        response = self.redis.xreadgroup(
            self.group_name,
            self.consumer_name,
            {self.stream_key: ">"},
            **kwargs,
        )
        if not response:
            return {
                "status": "idle",
                "received": 0,
                "reclaimed": 0,
                "applied": 0,
                "duplicate": 0,
                "stale": 0,
                "acknowledged": 0,
            }
        entries: list[tuple[Any, Any]] = []
        for returned_stream, messages in response:
            if _redis_text(returned_stream) != self.stream_key:
                raise ValueError("Redis returned an unexpected stream key.")
            entries.extend(messages)
        return self._apply_and_ack(entries, reclaimed=False)
