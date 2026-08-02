"""Runtime security configuration — fail closed on invalid production settings."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache


class SecurityConfigError(RuntimeError):
    """Raised when required security settings are missing or invalid."""


@dataclass(frozen=True)
class Settings:
    app_env: str
    oidc_mode: str  # static | jwks
    oidc_issuer: str
    oidc_audience: str
    oidc_jwks_url: str
    oidc_hs256_secret: str
    allow_anon_predict: bool
    model_bundle_path: str
    max_upload_bytes: int
    rate_limit_per_minute: int
    predict_timeout_sec: float
    top_k_max: int
    require_auth_for_ready: bool

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() in {"prod", "production"}


def _bool_env(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings(
        app_env=os.environ.get("APP_ENV", "development"),
        oidc_mode=os.environ.get("CIFAR_CNN_OIDC_MODE", "static").lower(),
        oidc_issuer=os.environ.get("OIDC_ISSUER", "https://cifar-cnn.local/test"),
        oidc_audience=os.environ.get("OIDC_AUDIENCE", "cifar-cnn-api"),
        oidc_jwks_url=os.environ.get("OIDC_JWKS_URL", ""),
        oidc_hs256_secret=os.environ.get(
            "CIFAR_CNN_OIDC_HS256_SECRET", "cifar-cnn-test-hs256-not-for-production"
        ),
        allow_anon_predict=_bool_env("CIFAR_CNN_ALLOW_ANON_PREDICT", False),
        model_bundle_path=os.environ.get(
            "MODEL_BUNDLE_PATH", "models/bundles/simple_cnn-1.0.1"
        ),
        max_upload_bytes=int(os.environ.get("CIFAR_CNN_MAX_UPLOAD_BYTES", str(1_000_000))),
        rate_limit_per_minute=int(os.environ.get("CIFAR_CNN_RATE_LIMIT_PER_MIN", "60")),
        predict_timeout_sec=float(os.environ.get("CIFAR_CNN_PREDICT_TIMEOUT_SEC", "5")),
        top_k_max=int(os.environ.get("CIFAR_CNN_TOP_K_MAX", "5")),
        require_auth_for_ready=_bool_env("CIFAR_CNN_AUTH_READY", False),
    )
    validate_settings(settings)
    return settings


def validate_settings(settings: Settings) -> None:
    if settings.oidc_mode not in {"static", "jwks"}:
        raise SecurityConfigError("CIFAR_CNN_OIDC_MODE must be 'static' or 'jwks'")
    if settings.allow_anon_predict and settings.is_production:
        raise SecurityConfigError(
            "Anonymous prediction cannot be enabled in production "
            "without formal risk acceptance path"
        )
    if settings.oidc_mode == "jwks":
        if not settings.oidc_issuer or not settings.oidc_audience or not settings.oidc_jwks_url:
            raise SecurityConfigError(
                "jwks mode requires OIDC_ISSUER, OIDC_AUDIENCE, and OIDC_JWKS_URL"
            )
    if settings.is_production and settings.oidc_mode == "static":
        raise SecurityConfigError("Production forbids static HS256 OIDC mode")
    if settings.max_upload_bytes < 1024 or settings.max_upload_bytes > 10_000_000:
        raise SecurityConfigError("CIFAR_CNN_MAX_UPLOAD_BYTES out of allowed range")
    if settings.rate_limit_per_minute < 1:
        raise SecurityConfigError("CIFAR_CNN_RATE_LIMIT_PER_MIN must be >= 1")
    if settings.top_k_max < 1 or settings.top_k_max > 10:
        raise SecurityConfigError("CIFAR_CNN_TOP_K_MAX must be in 1..10")


def reset_settings_cache() -> None:
    get_settings.cache_clear()
