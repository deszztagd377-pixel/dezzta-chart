from __future__ import annotations

import sqlite3

import pytest

from app.alert_device_store import (
    AlertDeviceQuotaExceeded,
    AlertDeviceStoreError,
    SQLiteAlertDeviceStore,
)


@pytest.fixture
def store(tmp_path):
    return SQLiteAlertDeviceStore(
        str(tmp_path / "registry.sqlite3"),
        encryption_key=b"K" * 32,
    )


def test_registration_encrypts_token_and_supports_internal_delivery_lookup(store):
    token = "fcm-secret-token-value"
    store.register(owner_id="firebase-user-a", installation_id="phone-1", fcm_token=token)

    with sqlite3.connect(store.database_path) as connection:
        ciphertext = connection.execute(
            "SELECT token_ciphertext FROM alert_device_tokens"
        ).fetchone()[0]

    assert isinstance(ciphertext, bytes)
    assert token.encode() not in ciphertext
    assert store.token_for_delivery(
        owner_id="firebase-user-a", installation_id="phone-1"
    ) == token
    assert store.active_count(owner_id="firebase-user-a") == 1


def test_token_rotation_replaces_ciphertext_without_creating_another_device(store):
    store.register(owner_id="account-a", installation_id="phone-1", fcm_token="old-token")
    store.register(owner_id="account-a", installation_id="phone-1", fcm_token="new-token")

    assert store.active_count(owner_id="account-a") == 1
    assert store.token_for_delivery(
        owner_id="account-a", installation_id="phone-1"
    ) == "new-token"


def test_owner_scope_prevents_cross_account_token_lookup_or_revocation(store):
    store.register(owner_id="account-a", installation_id="phone-1", fcm_token="private-token")

    assert store.token_for_delivery(
        owner_id="account-b", installation_id="phone-1"
    ) is None
    assert not store.revoke(owner_id="account-b", installation_id="phone-1")
    assert store.token_for_delivery(
        owner_id="account-a", installation_id="phone-1"
    ) == "private-token"


def test_revoked_device_is_not_deliverable_and_can_be_registered_again(store):
    store.register(owner_id="account-a", installation_id="phone-1", fcm_token="token-v1")
    assert store.revoke(owner_id="account-a", installation_id="phone-1")
    assert not store.revoke(owner_id="account-a", installation_id="phone-1")
    assert store.token_for_delivery(
        owner_id="account-a", installation_id="phone-1"
    ) is None

    store.register(owner_id="account-a", installation_id="phone-1", fcm_token="token-v2")
    assert store.token_for_delivery(
        owner_id="account-a", installation_id="phone-1"
    ) == "token-v2"
    assert store.active_count(owner_id="account-a") == 1


def test_account_device_quota_is_ten_and_isolated_per_owner(store):
    for index in range(10):
        store.register(
            owner_id="account-a",
            installation_id=f"phone-{index}",
            fcm_token=f"token-{index}",
        )

    with pytest.raises(AlertDeviceQuotaExceeded):
        store.register(
            owner_id="account-a", installation_id="phone-overflow", fcm_token="overflow"
        )

    store.register(
        owner_id="account-b", installation_id="phone-1", fcm_token="other-account-token"
    )
    assert store.active_count(owner_id="account-a") == 10
    assert store.active_count(owner_id="account-b") == 1


def test_reactivation_cannot_bypass_active_device_quota(store):
    store.register(owner_id="account-a", installation_id="phone-0", fcm_token="token-0")
    store.revoke(owner_id="account-a", installation_id="phone-0")
    for index in range(1, 11):
        store.register(
            owner_id="account-a",
            installation_id=f"phone-{index}",
            fcm_token=f"token-{index}",
        )

    with pytest.raises(AlertDeviceQuotaExceeded):
        store.register(owner_id="account-a", installation_id="phone-0", fcm_token="rotated")


def test_ciphertext_authentication_fails_with_wrong_key(tmp_path):
    path = str(tmp_path / "registry.sqlite3")
    first = SQLiteAlertDeviceStore(path, encryption_key=b"A" * 32)
    first.register(owner_id="account-a", installation_id="phone-1", fcm_token="secret")

    second = SQLiteAlertDeviceStore(path, encryption_key=b"B" * 32)
    with pytest.raises(AlertDeviceStoreError):
        second.token_for_delivery(owner_id="account-a", installation_id="phone-1")


@pytest.mark.parametrize("key", [b"", b"x" * 31, b"x" * 33, "x" * 32])
def test_encryption_key_must_be_exactly_32_bytes(tmp_path, key):
    with pytest.raises(ValueError, match="exactly 32 bytes"):
        SQLiteAlertDeviceStore(str(tmp_path / "db.sqlite3"), encryption_key=key)


@pytest.mark.parametrize("token", ["", "  ", "bad token", "x" * 4097])
def test_invalid_fcm_tokens_are_rejected(store, token):
    with pytest.raises(ValueError, match="fcm_token"):
        store.register(owner_id="account-a", installation_id="phone-1", fcm_token=token)


def test_active_tokens_for_delivery_are_owner_scoped_and_exclude_revoked(store):
    store.register(owner_id="account-a", installation_id="phone-a1", fcm_token="token-a1")
    store.register(owner_id="account-a", installation_id="phone-a2", fcm_token="token-a2")
    store.register(owner_id="account-b", installation_id="phone-b1", fcm_token="token-b1")
    store.revoke(owner_id="account-a", installation_id="phone-a1")

    devices = store.active_tokens_for_delivery(owner_id="account-a")

    assert [(device.installation_id, device.token) for device in devices] == [
        ("phone-a2", "token-a2")
    ]


def test_active_tokens_for_delivery_enforces_a_small_limit(store):
    for index in range(3):
        store.register(
            owner_id="account-a",
            installation_id=f"phone-{index}",
            fcm_token=f"token-{index}",
        )

    devices = store.active_tokens_for_delivery(owner_id="account-a", limit=2)
    assert len(devices) == 2
    assert all(device.installation_id.startswith("phone-") for device in devices)


@pytest.mark.parametrize("limit", [0, 11, True, -1])
def test_active_tokens_for_delivery_rejects_invalid_limits(store, limit):
    with pytest.raises(ValueError, match="limit"):
        store.active_tokens_for_delivery(owner_id="account-a", limit=limit)
