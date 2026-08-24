"""Shared authentication helpers for all orderflow services."""
import base64
import hashlib
import hmac
import json
import os
import time

SIGNING_KEY = os.environ.get("ORDERFLOW_SIGNING_KEY", "dev-only-key")


class AuthError(Exception):
    """Raised when a token is missing, malformed, or expired."""


def decode_jwt(token: str) -> dict:
    """Decode and verify a compact JWS token (HS256). Returns the claims dict.

    Raises AuthError on any structural or signature problem — callers should
    never see a half-decoded token.
    """
    try:
        header_b64, payload_b64, sig_b64 = token.split(".")
    except ValueError:
        raise AuthError("malformed token: expected three dot-separated parts")

    signing_input = f"{header_b64}.{payload_b64}".encode()
    expected = base64.urlsafe_b64encode(
        hmac.new(SIGNING_KEY.encode(), signing_input, hashlib.sha256).digest()
    ).rstrip(b"=").decode()
    if not hmac.compare_digest(expected, sig_b64):
        raise AuthError("signature mismatch")

    padded = payload_b64 + "=" * (-len(payload_b64) % 4)
    claims = json.loads(base64.urlsafe_b64decode(padded))
    if claims.get("exp", 0) < time.time():
        raise AuthError("token expired")
    return claims


def verify_token(token: str | None) -> dict:
    """Entry point used by every service route. Returns claims or raises AuthError."""
    if not token:
        raise AuthError("missing bearer token")
    return decode_jwt(token.removeprefix("Bearer ").strip())
