"""Provider-neutral identity verification with Firebase Admin as prototype IdP.

No HTTP route is enabled by this module. Callers must derive account ownership
only from the returned verified principal, never from request-supplied owner IDs.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


class IdentityVerificationError(ValueError):
    """The presented identity token is invalid, expired, revoked, or malformed."""


class IdentityProviderUnavailable(RuntimeError):
    """Server identity verification is not configured or cannot initialize."""


@dataclass(frozen=True, slots=True)
class VerifiedPrincipal:
    subject: str
    issuer: str
    audience: str
    auth_time: int


class FirebaseIdentityVerifier:
    """Verify Firebase ID tokens using Admin SDK and application credentials.

    The optional callable is a narrow test seam. Production callers should not
    supply it; Firebase Admin validates signature, issuer, audience and expiry,
    while check_revoked=True enforces refresh-token revocation checks.
    """

    def __init__(
        self,
        project_id: str,
        *,
        verify_callable: Callable[..., dict[str, Any]] | None = None,
    ) -> None:
        self._project_id = project_id.strip() if isinstance(project_id, str) else ""
        self._verify_callable = verify_callable
        self._firebase_app = None

    def _get_verify_callable(self) -> Callable[..., dict[str, Any]]:
        if not self._project_id:
            raise IdentityProviderUnavailable(
                "Firebase identity verification is not configured."
            )
        if self._verify_callable is not None:
            return self._verify_callable
        try:
            import firebase_admin
            from firebase_admin import auth
        except ImportError as exc:
            raise IdentityProviderUnavailable(
                "Firebase Admin SDK is unavailable."
            ) from exc

        if self._firebase_app is None:
            try:
                self._firebase_app = firebase_admin.get_app(self._project_id)
            except ValueError:
                try:
                    self._firebase_app = firebase_admin.initialize_app(
                        options={"projectId": self._project_id},
                        name=self._project_id,
                    )
                except Exception as exc:
                    raise IdentityProviderUnavailable(
                        "Firebase identity provider could not initialize."
                    ) from exc
        return lambda token, **kwargs: auth.verify_id_token(
            token, app=self._firebase_app, **kwargs
        )

    def verify(self, token: str) -> VerifiedPrincipal:
        if not isinstance(token, str) or not token or len(token) > 16_384:
            raise IdentityVerificationError("A valid identity token is required.")
        verify_callable = self._get_verify_callable()
        try:
            claims = verify_callable(token, check_revoked=True)
        except IdentityProviderUnavailable:
            raise
        except Exception as exc:
            # Do not propagate SDK details, token fragments, or credential data.
            raise IdentityVerificationError("Identity token verification failed.") from exc

        if not isinstance(claims, dict):
            raise IdentityVerificationError("Identity token claims are invalid.")
        subject = claims.get("uid") if "uid" in claims else claims.get("sub")
        issuer = claims.get("iss")
        audience = claims.get("aud")
        auth_time = claims.get("auth_time")
        expected_issuer = f"https://securetoken.google.com/{self._project_id}"
        if (
            not isinstance(subject, str) or not subject.strip() or len(subject) > 128
            or issuer != expected_issuer
            or audience != self._project_id
            or not isinstance(auth_time, int) or isinstance(auth_time, bool) or auth_time <= 0
            # Firebase Admin exposes both the JWT subject and uid; they must
            # identify the same account before a principal can be constructed.
            or (
                "uid" in claims and "sub" in claims
                and claims.get("uid") != claims.get("sub")
            )
        ):
            raise IdentityVerificationError("Identity token claims are invalid.")
        return VerifiedPrincipal(
            subject=subject,
            issuer=issuer,
            audience=audience,
            auth_time=auth_time,
        )
