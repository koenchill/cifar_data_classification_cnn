"""In-memory fixed-window rate limiter (per subject)."""

from __future__ import annotations

import threading
import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request, status

from cifar_cnn.api.auth import Principal
from cifar_cnn.api.config import Settings, get_settings


class RateLimiter:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def check(self, key: str, limit: int, window_sec: float = 60.0) -> None:
        now = time.monotonic()
        with self._lock:
            q = self._hits[key]
            while q and now - q[0] > window_sec:
                q.popleft()
            if len(q) >= limit:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="rate_limit_exceeded",
                    headers={"Retry-After": "60"},
                )
            q.append(now)

    def reset(self) -> None:
        with self._lock:
            self._hits.clear()


_limiter = RateLimiter()


def get_rate_limiter() -> RateLimiter:
    return _limiter


async def enforce_predict_rate_limit(
    request: Request,
    principal: Principal,
    settings: Settings | None = None,
) -> None:
    settings = settings or get_settings()
    key = f"predict:{principal.subject}"
    get_rate_limiter().check(key, settings.rate_limit_per_minute)
    request.state.rate_limit_key = key
