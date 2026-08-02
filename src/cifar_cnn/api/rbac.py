"""Deny-by-default RBAC helpers."""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from fastapi import Depends, HTTPException, status

from cifar_cnn.api.auth import Principal, require_principal


def require_scopes(*required: str) -> Callable[..., Awaitable[Principal]]:
    """Return a dependency that enforces all listed scopes (AND)."""

    async def _dep(principal: Principal = Depends(require_principal)) -> Principal:
        missing = [s for s in required if not principal.has_scope(s)]
        if missing:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="insufficient_scope",
            )
        return principal

    return _dep
