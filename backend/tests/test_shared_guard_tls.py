from types import SimpleNamespace

from redis.asyncio import Redis

from app.shared_guard import RedisSharedGuard


def test_rediss_guard_requires_ca_validation_and_hostname_verification(monkeypatch):
    captured = {}

    def fake_from_url(cls, url, **options):
        captured["url"] = url
        captured["options"] = options
        return SimpleNamespace()

    monkeypatch.setattr(Redis, "from_url", classmethod(fake_from_url))

    guard = RedisSharedGuard(
        "rediss://guard-user:guard-password@redis.example:6380/0"
    )

    assert guard._redis is not None
    assert captured["url"] == "rediss://guard-user:guard-password@redis.example:6380/0"
    assert captured["options"]["ssl_cert_reqs"] == "required"
    assert captured["options"]["ssl_check_hostname"] is True
    assert captured["options"]["socket_connect_timeout"] == 2
    assert captured["options"]["socket_timeout"] == 2


def test_plain_redis_guard_does_not_silently_enable_tls_options(monkeypatch):
    captured = {}

    def fake_from_url(cls, url, **options):
        captured["url"] = url
        captured["options"] = options
        return SimpleNamespace()

    monkeypatch.setattr(Redis, "from_url", classmethod(fake_from_url))

    RedisSharedGuard("redis://localhost:6379/0")

    assert captured["url"] == "redis://localhost:6379/0"
    assert "ssl_cert_reqs" not in captured["options"]
    assert "ssl_check_hostname" not in captured["options"]
