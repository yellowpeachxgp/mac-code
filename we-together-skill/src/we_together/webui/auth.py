"""Bearer-token auth helpers for the host-local WebUI."""

from __future__ import annotations

import ipaddress
from dataclasses import dataclass

from we_together.services.federation_security import RateLimiter, hash_token, verify_token


@dataclass
class AuthResult:
    ok: bool
    status: int = 200
    code: str = ""
    message: str = ""
    key: str = ""


def is_loopback_host(host: str) -> bool:
    normalized = (host or "").strip().lower()
    if normalized in {"localhost", "127.0.0.1", "::1"}:
        return True
    try:
        return ipaddress.ip_address(normalized).is_loopback
    except ValueError:
        return False


class BearerTokenAuth:
    def __init__(self, token: str | None, *, rate_limit_per_minute: int = 120):
        self._token_hashes = [hash_token(token)] if token else []
        self._limiter = RateLimiter(max_per_minute=rate_limit_per_minute)

    @property
    def mode(self) -> str:
        return "bearer" if self._token_hashes else "token_required"

    def authenticate(self, authorization_header: str | None) -> AuthResult:
        if not self._token_hashes:
            return AuthResult(
                ok=False,
                status=401,
                code="token_not_configured",
                message="WebUI API requires a configured bearer token.",
            )

        prefix = "Bearer "
        if not authorization_header or not authorization_header.startswith(prefix):
            return AuthResult(
                ok=False,
                status=401,
                code="unauthorized",
                message="Missing Authorization: Bearer token.",
            )

        provided = authorization_header[len(prefix):].strip()
        if not verify_token(provided, self._token_hashes):
            return AuthResult(
                ok=False,
                status=401,
                code="unauthorized",
                message="Invalid bearer token.",
            )

        key = hash_token(provided)
        if not self._limiter.allow(key):
            return AuthResult(
                ok=False,
                status=429,
                code="rate_limited",
                message="Too many WebUI requests for this token.",
                key=key,
            )
        return AuthResult(ok=True, key=key)
