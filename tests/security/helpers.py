"""Shared helpers for API security/contract/e2e tests."""

from __future__ import annotations

import io
import time

import jwt
from PIL import Image

ISSUER = "https://cifar-cnn.local/test"
AUDIENCE = "cifar-cnn-api"
SECRET = "cifar-cnn-test-hs256-not-for-production"


def mint_token(
    *,
    sub: str = "user-1",
    scopes: str = "predict:invoke metadata:read",
    roles: list[str] | None = None,
    exp_delta: int = 3600,
    secret: str = SECRET,
    issuer: str = ISSUER,
    audience: str = AUDIENCE,
) -> str:
    now = int(time.time())
    payload: dict[str, object] = {
        "sub": sub,
        "iss": issuer,
        "aud": audience,
        "iat": now,
        "exp": now + exp_delta,
        "scope": scopes,
    }
    if roles:
        payload["roles"] = roles
    return jwt.encode(payload, secret, algorithm="HS256")


def png_bytes(
    size: tuple[int, int] = (32, 32),
    color: tuple[int, int, int] = (10, 20, 30),
) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", size, color).save(buf, format="PNG")
    return buf.getvalue()


def auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}
