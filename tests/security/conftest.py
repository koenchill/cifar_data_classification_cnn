"""Shared fixtures for API security tests."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from cifar_cnn.api.app import create_app
from cifar_cnn.api.audit import get_audit_sink
from cifar_cnn.api.config import Settings, reset_settings_cache
from cifar_cnn.api.rate_limit import get_rate_limiter
from cifar_cnn.api.runtime import ModelRuntime
from tests.security.helpers import AUDIENCE, ISSUER, SECRET

REPO_ROOT = Path(__file__).resolve().parents[2]
BUNDLE_PATH = REPO_ROOT / "models" / "bundles" / "simple_cnn-1.0.1"


@pytest.fixture
def api_settings() -> Settings:
    reset_settings_cache()
    return Settings(
        app_env="development",
        oidc_mode="static",
        oidc_issuer=ISSUER,
        oidc_audience=AUDIENCE,
        oidc_jwks_url="",
        oidc_hs256_secret=SECRET,
        allow_anon_predict=False,
        model_bundle_path=str(BUNDLE_PATH),
        max_upload_bytes=50_000,
        rate_limit_per_minute=5,
        predict_timeout_sec=10.0,
        top_k_max=5,
        require_auth_for_ready=False,
    )


@pytest.fixture
def client(api_settings: Settings) -> Iterator[TestClient]:
    get_rate_limiter().reset()
    get_audit_sink().reset()
    runtime = ModelRuntime()
    app = create_app(settings=api_settings, runtime=runtime, load_model_on_startup=True)
    with TestClient(app) as c:
        yield c
    get_rate_limiter().reset()
    get_audit_sink().reset()
    reset_settings_cache()
