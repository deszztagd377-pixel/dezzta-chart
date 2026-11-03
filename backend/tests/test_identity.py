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
