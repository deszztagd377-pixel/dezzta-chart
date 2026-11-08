import pytest

from app.identity import (
    FirebaseIdentityVerifier,
    IdentityProviderUnavailable,
    IdentityVerificationError,
)

PROJECT = "dezzta-chart-prod"
CLAIMS = {
    "uid": "firebase-user-123",
    "sub": "firebase-user-123",
    "iss": f"https://securetoken.google.com/{PROJECT}",
    "aud": PROJECT,
    "auth_time": 1_798_000_000,
}


def test_verifier_returns_principal_only_after_verified_claims():
    calls = []

    def fake_verify(token, **kwargs):
        calls.append((token, kwargs))
        return CLAIMS

    principal = FirebaseIdentityVerifier(
        PROJECT, verify_callable=fake_verify
    ).verify("signed-firebase-id-token")

    assert principal.subject == "firebase-user-123"
    assert principal.issuer == CLAIMS["iss"]
    assert principal.audience == PROJECT
    assert principal.auth_time == CLAIMS["auth_time"]
    assert calls == [("signed-firebase-id-token", {"check_revoked": True})]


@pytest.mark.parametrize(
    "overrides",
    [
        {"iss": "https://attacker.example"},
        {"aud": "another-project"},
        {"uid": ""},
        {"sub": "different-firebase-user"},
        {"auth_time": True},
        {"auth_time": 0},
    ],
)
def test_invalid_claims_are_rejected(overrides):
    claims = {**CLAIMS, **overrides}
    verifier = FirebaseIdentityVerifier(
        PROJECT, verify_callable=lambda token, **kwargs: claims
    )

    with pytest.raises(IdentityVerificationError):
        verifier.verify("token")


def test_sdk_errors_are_normalized_without_leaking_details():
    def rejected(token, **kwargs):
        raise RuntimeError("sensitive SDK detail and token=secret")

    verifier = FirebaseIdentityVerifier(PROJECT, verify_callable=rejected)
    with pytest.raises(IdentityVerificationError) as error:
        verifier.verify("invalid-token")

    assert str(error.value) == "Identity token verification failed."
    assert "secret" not in str(error.value)


@pytest.mark.parametrize("token", ["", None, 7, "x" * 16_385])
def test_malformed_or_oversized_tokens_are_rejected_before_sdk(token):
    verifier = FirebaseIdentityVerifier(
        PROJECT,
        verify_callable=lambda token, **kwargs: pytest.fail("SDK must not be called"),
    )
    with pytest.raises(IdentityVerificationError):
        verifier.verify(token)


def test_missing_project_configuration_fails_closed():
    verifier = FirebaseIdentityVerifier(
        "", verify_callable=lambda token, **kwargs: CLAIMS
    )
    with pytest.raises(IdentityProviderUnavailable):
        verifier.verify("token")

def _install_fake_firebase_admin(monkeypatch, *, get_app, initialize_app, verify_id_token):
    import sys
    from types import ModuleType

    admin = ModuleType("firebase_admin")
    auth = ModuleType("firebase_admin.auth")
    admin.get_app = get_app
    admin.initialize_app = initialize_app
    auth.verify_id_token = verify_id_token
    admin.auth = auth
    monkeypatch.setitem(sys.modules, "firebase_admin", admin)
    monkeypatch.setitem(sys.modules, "firebase_admin.auth", auth)


def test_admin_sdk_reuses_named_project_app_and_enforces_revocation_check(monkeypatch):
    app = object()
    calls = []

    def verify_id_token(token, *, app, check_revoked):
        calls.append((token, app, check_revoked))
        return CLAIMS

    _install_fake_firebase_admin(
        monkeypatch,
        get_app=lambda name: app if name == PROJECT else pytest.fail("unexpected project"),
        initialize_app=lambda **kwargs: pytest.fail("existing app should be reused"),
        verify_id_token=verify_id_token,
    )

    verifier = FirebaseIdentityVerifier(PROJECT)
    assert verifier.verify("first-token").subject == "firebase-user-123"
    assert verifier.verify("second-token").subject == "firebase-user-123"
    assert calls == [
        ("first-token", app, True),
        ("second-token", app, True),
    ]


def test_admin_sdk_initializes_missing_named_project_app(monkeypatch):
    app = object()
    initialized = []
    verified = []

    def get_app(name):
        assert name == PROJECT
        raise ValueError("app does not exist")

    def initialize_app(*, options, name):
        initialized.append((options, name))
        return app

    def verify_id_token(token, *, app, check_revoked):
        verified.append((token, app, check_revoked))
        return CLAIMS

    _install_fake_firebase_admin(
        monkeypatch,
        get_app=get_app,
        initialize_app=initialize_app,
        verify_id_token=verify_id_token,
    )

    principal = FirebaseIdentityVerifier(PROJECT).verify("valid-token")
    assert principal.subject == "firebase-user-123"
    assert initialized == [({"projectId": PROJECT}, PROJECT)]
    assert verified == [("valid-token", app, True)]


def test_admin_sdk_initialization_failure_is_normalized(monkeypatch):
    def get_app(name):
        raise ValueError("missing app")

    def initialize_app(**kwargs):
        raise RuntimeError("private key material must not escape")

    _install_fake_firebase_admin(
        monkeypatch,
        get_app=get_app,
        initialize_app=initialize_app,
        verify_id_token=lambda *args, **kwargs: pytest.fail("verification must not run"),
    )

    with pytest.raises(IdentityProviderUnavailable) as error:
        FirebaseIdentityVerifier(PROJECT).verify("token")

    assert str(error.value) == "Firebase identity provider could not initialize."
    assert "private key" not in str(error.value)


def test_admin_sdk_import_failure_is_reported_as_provider_unavailable(monkeypatch):
    import sys

    monkeypatch.setitem(sys.modules, "firebase_admin", None)
    monkeypatch.setitem(sys.modules, "firebase_admin.auth", None)

    with pytest.raises(IdentityProviderUnavailable) as error:
        FirebaseIdentityVerifier(PROJECT).verify("token")

    assert str(error.value) == "Firebase Admin SDK is unavailable."
