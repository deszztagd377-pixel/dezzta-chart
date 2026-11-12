[object Object]

def test_rediss_client_enforces_certificate_and_hostname_validation(monkeypatch):
    from redis.asyncio import Redis

    captured = {}

    def fake_from_url(cls, url, **options):
        captured["url"] = url
        captured["options"] = options
        return FakeRedis()

    monkeypatch.setattr(Redis, "from_url", classmethod(fake_from_url))

    RedisSharedGuard("rediss://redis.example.invalid:6380/0")

    assert captured["url"] == "rediss://redis.example.invalid:6380/0"
    assert captured["options"]["ssl_cert_reqs"] == "required"
    assert captured["options"]["ssl_check_hostname"] is True
    assert captured["options"]["socket_connect_timeout"] == 2
