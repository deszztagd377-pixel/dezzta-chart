from __future__ import annotations

import threading
import time

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


def make_settings(tmp_path):
    return Settings(
        app_env="test",
        market_data_ws_token="test-secret",
        cors_allowed_origins=("http://localhost:5173",),
        instrument_registry_db_path=str(tmp_path / "publisher-lifecycle.sqlite3"),
    )


class FakeRedis:
    def __init__(self):
        self.pinged = False
        self.closed = False

    def ping(self):
        self.pinged = True
        return True

    def close(self):
        self.closed = True


class FakePublisher:
    def __init__(self, redis_client):
        self.appender = type(
            "FakeAppender", (), {"redis": redis_client, "stream_key": "test:ohlcv"}
        )()
        self.called = threading.Event()
        self.calls = 0

    def publish_available(self):
        self.calls += 1
        self.called.set()
        return {
            "status": "idle",
            "published": 0,
            "verified_existing": 0,
            "published_cursor": 0,
            "high_water": 0,
            "has_more": False,
        }


def test_publisher_runtime_is_pinged_started_and_closed_by_lifespan(tmp_path):
    redis_client = FakeRedis()
    publisher = FakePublisher(redis_client)

    def runtime_factory(source_store):
        assert source_store.database_path == str(tmp_path / "publisher-lifecycle.sqlite3")
        return {
            "publisher": publisher,
            "redis_client": redis_client,
            "stream_key": "test:ohlcv",
        }

    application = create_app(
        make_settings(tmp_path),
        publisher_runtime_factory=runtime_factory,
    )

    with TestClient(application):
        assert redis_client.pinged is True
        assert publisher.called.wait(timeout=2.0)
        for _ in range(100):
            if application.state.ohlcv_publisher_status["state"] == "running":
                break
            time.sleep(0.01)
        assert application.state.ohlcv_publisher is publisher
        assert application.state.ohlcv_publisher_status["enabled"] is True
        assert application.state.ohlcv_publisher_status["state"] == "running"

    assert redis_client.closed is True
    assert application.state.ohlcv_publisher is None


def test_publisher_and_gateway_roles_cannot_be_combined(tmp_path):
    with pytest.raises(ValueError, match="separate app roles"):
        create_app(
            make_settings(tmp_path),
            publisher_runtime_factory=lambda store: {},
            replica_runtime_factory=lambda: {},
        )


def test_publisher_runtime_mismatch_fails_startup_without_accepting_traffic(tmp_path):
    redis_client = FakeRedis()
    publisher = FakePublisher(redis_client)

    application = create_app(
        make_settings(tmp_path),
        publisher_runtime_factory=lambda store: {
            "publisher": publisher,
            "redis_client": redis_client,
            "stream_key": "different:stream",
        },
    )

    with pytest.raises(RuntimeError, match="does not match"):
        with TestClient(application):
            pass

    assert redis_client.closed is True
