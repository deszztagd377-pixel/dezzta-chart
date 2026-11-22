from __future__ import annotations

import asyncio
import os

import pytest
import redis

from app.shared_guard import RedisSharedGuard


@pytest.fixture
def tls_test_material():
    url = os.environ.get("REDIS_TLS_TEST_URL", "")
    ca_path = os.environ.get("REDIS_TLS_TEST_CA", "")
    wrong_ca_path = os.environ.get("REDIS_TLS_TEST_WRONG_CA", "")
    if not url or not ca_path or not wrong_ca_path:
        pytest.skip("The isolated Redis TLS CI fixture is not configured.")
    return url, ca_path, wrong_ca_path


def test_real_redis_tls_ca_hostname_acl_and_shared_guard_operations(tls_test_material):
    """Exercise a real TLS-only Redis listener, including negative certificate cases."""
    url, ca_path, wrong_ca_path = tls_test_material

    async def exercise_valid_connection():
        guard = RedisSharedGuard(url, redis_tls_ca_certs=ca_path)
        try:
            await guard.start()
            allowed, retry_after = await guard.allow_http("redis-tls-ci-client")
            assert (allowed, retry_after) == (True, 0)

            ticket = await guard.issue_websocket_ticket("redis-tls-ci-account")
            assert await guard.consume_websocket_ticket(ticket) == "redis-tls-ci-account"

            assert await guard.acquire_websocket(
                "redis-tls-ci-connection", "redis-tls-ci-account"
            )
            assert await guard.renew_websocket(
                "redis-tls-ci-connection", "redis-tls-ci-account"
            )
            await guard.release_websocket(
                "redis-tls-ci-connection", "redis-tls-ci-account"
            )
        finally:
            await guard.close()

    async def assert_tls_rejected(bad_url: str, ca_bundle: str):
        guard = RedisSharedGuard(bad_url, redis_tls_ca_certs=ca_bundle)
        try:
            with pytest.raises(redis.exceptions.ConnectionError):
                await guard.start()
        finally:
            await guard.close()

    async def run():
        await exercise_valid_connection()

        # The CA is trusted, but the certificate is valid only for DNS:localhost.
        wrong_hostname_url = url.replace("@localhost:", "@127.0.0.1:", 1)
        assert wrong_hostname_url != url
        await assert_tls_rejected(wrong_hostname_url, ca_path)

        # The hostname is correct, but the issuing CA is not trusted.
        await assert_tls_rejected(url, wrong_ca_path)

        # The fixture has no plaintext Redis listener; no protocol downgrade is allowed.
        plaintext_url = url.replace("rediss://", "redis://", 1)
        await assert_tls_rejected(plaintext_url, "")

    asyncio.run(run())
