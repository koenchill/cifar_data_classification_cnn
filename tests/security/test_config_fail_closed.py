"""Security settings fail closed for production misconfig."""

from __future__ import annotations

import pytest

from cifar_cnn.api.config import SecurityConfigError, Settings, validate_settings


def test_prod_forbids_static_oidc() -> None:
    settings = Settings(
        app_env="production",
        oidc_mode="static",
        oidc_issuer="https://idp.example",
        oidc_audience="api",
        oidc_jwks_url="",
        oidc_hs256_secret="x",
        allow_anon_predict=False,
        model_bundle_path="models/bundles/x",
        max_upload_bytes=1000,
        rate_limit_per_minute=10,
        predict_timeout_sec=1.0,
        top_k_max=3,
        require_auth_for_ready=False,
    )
    with pytest.raises(SecurityConfigError):
        validate_settings(settings)


def test_prod_forbids_anon_predict() -> None:
    settings = Settings(
        app_env="production",
        oidc_mode="jwks",
        oidc_issuer="https://idp.example",
        oidc_audience="api",
        oidc_jwks_url="https://idp.example/jwks",
        oidc_hs256_secret="x",
        allow_anon_predict=True,
        model_bundle_path="models/bundles/x",
        max_upload_bytes=1000,
        rate_limit_per_minute=10,
        predict_timeout_sec=1.0,
        top_k_max=3,
        require_auth_for_ready=False,
    )
    with pytest.raises(SecurityConfigError):
        validate_settings(settings)


def test_jwks_requires_urls() -> None:
    settings = Settings(
        app_env="development",
        oidc_mode="jwks",
        oidc_issuer="",
        oidc_audience="api",
        oidc_jwks_url="",
        oidc_hs256_secret="x",
        allow_anon_predict=False,
        model_bundle_path="models/bundles/x",
        max_upload_bytes=1000,
        rate_limit_per_minute=10,
        predict_timeout_sec=1.0,
        top_k_max=3,
        require_auth_for_ready=False,
    )
    with pytest.raises(SecurityConfigError):
        validate_settings(settings)
