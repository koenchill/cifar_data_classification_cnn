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
from cifar_cnn.inference.bundle import pack_bundle
from cifar_cnn.models.simple_cnn import SimpleCNN
from tests.security.helpers import AUDIENCE, ISSUER, SECRET


@pytest.fixture
def bundle_dir(tmp_path: Path) -> Path:
    """Ephemeral signed bundle — avoids committed CRLF/hash platform drift."""
    root = tmp_path / "api-test-bundle"
    pack_bundle(
        SimpleCNN(),
        root,
        bundle_id="api-test",
        version="0.0.1",
        run_parity=False,
    )
    return root


@pytest.fixture
def api_settings(bundle_dir: Path) -> Settings:
    reset_settings_cache()
    return Settings(
        app_env="development",
        oidc_mode="static",
        oidc_issuer=ISSUER,
        oidc_audience=AUDIENCE,
        oidc_jwks_url="",
        oidc_hs256_secret=SECRET,
        allow_anon_predict=False,
        model_bundle_path=str(bundle_dir),
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
