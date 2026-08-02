"""OIDC/JWT authentication — deny by default when credentials are missing/invalid."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, cast

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient

from cifar_cnn.api.config import Settings, get_settings

_bearer = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class Principal:
    subject: str
    scopes: frozenset[str] = field(default_factory=frozenset)
    roles: frozenset[str] = field(default_factory=frozenset)
    token_id: str | None = None

    def has_scope(self, scope: str) -> bool:
        return scope in self.scopes or "admin" in self.roles or "admin:*" in self.scopes


ROLE_SCOPE_MAP: dict[str, frozenset[str]] = {
    "predictor": frozenset({"predict:invoke", "metadata:read"}),
    "viewer": frozenset({"metadata:read", "health:read"}),
    "admin": frozenset(
        {"predict:invoke", "metadata:read", "health:read", "admin:reload"}
    ),
}


def _scopes_from_claims(claims: dict[str, Any]) -> frozenset[str]:
    scopes: set[str] = set()
    scope_claim = claims.get("scope") or claims.get("scp") or ""
    if isinstance(scope_claim, str):
        scopes.update(s for s in scope_claim.split() if s)
    elif isinstance(scope_claim, list):
        scopes.update(str(s) for s in scope_claim)
    roles = claims.get("roles") or claims.get("role") or []
    if isinstance(roles, str):
        roles = [roles]
    for role in roles:
        scopes.update(ROLE_SCOPE_MAP.get(str(role), frozenset()))
    return frozenset(scopes)


def decode_token(token: str, settings: Settings) -> dict[str, Any]:
    options = {
        "require": ["exp", "iss", "aud", "sub"],
        "verify_aud": True,
        "verify_iss": True,
        "verify_exp": True,
    }
    if settings.oidc_mode == "static":
        return cast(
            dict[str, Any],
            jwt.decode(
                token,
                settings.oidc_hs256_secret,
                algorithms=["HS256"],
                audience=settings.oidc_audience,
                issuer=settings.oidc_issuer,
                options=options,
            ),
        )
    jwks_client = PyJWKClient(settings.oidc_jwks_url, cache_keys=True)
    signing_key = jwks_client.get_signing_key_from_jwt(token)
    return cast(
        dict[str, Any],
        jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=settings.oidc_audience,
            issuer=settings.oidc_issuer,
            options=options,
        ),
    )


def principal_from_token(token: str, settings: Settings | None = None) -> Principal:
    settings = settings or get_settings()
    try:
        claims = decode_token(token, settings)
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="token_expired",
        ) from exc
    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid_token",
        ) from exc
    subject = str(claims.get("sub", ""))
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid_token",
        )
    roles_raw = claims.get("roles") or claims.get("role") or []
    if isinstance(roles_raw, str):
        roles_raw = [roles_raw]
    return Principal(
        subject=subject,
        scopes=_scopes_from_claims(claims),
        roles=frozenset(str(r) for r in roles_raw),
        token_id=str(claims["jti"]) if claims.get("jti") else None,
    )


def settings_from_request(request: Request) -> Settings:
    configured = getattr(request.app.state, "settings", None)
    if isinstance(configured, Settings):
        return configured
    return get_settings()


async def optional_principal(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> Principal | None:
    if credentials is None or credentials.scheme.lower() != "bearer":
        return None
    return principal_from_token(credentials.credentials, settings_from_request(request))


async def require_principal(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> Principal:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="missing_bearer_token",
        )
    return principal_from_token(credentials.credentials, settings_from_request(request))


def bind_request_principal(request: Request, principal: Principal | None) -> None:
    request.state.principal = principal
