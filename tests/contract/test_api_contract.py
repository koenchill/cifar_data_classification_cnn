"""HTTP contract for health, ready, metadata, and predict."""

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
from tests.security.helpers import AUDIENCE, ISSUER, SECRET, auth_header, mint_token, png_bytes


@pytest.fixture
def client(tmp_path: Path) -> Iterator[TestClient]:
    reset_settings_cache()
    get_rate_limiter().reset()
    get_audit_sink().reset()
    bundle = tmp_path / "contract-bundle"
    pack_bundle(
        SimpleCNN(),
        bundle,
        bundle_id="contract",
        version="0.0.1",
        run_parity=False,
    )
    settings = Settings(
        app_env="development",
        oidc_mode="static",
        oidc_issuer=ISSUER,
        oidc_audience=AUDIENCE,
        oidc_jwks_url="",
        oidc_hs256_secret=SECRET,
        allow_anon_predict=False,
        model_bundle_path=str(bundle),
        max_upload_bytes=1_000_000,
        rate_limit_per_minute=120,
        predict_timeout_sec=10.0,
        top_k_max=5,
        require_auth_for_ready=False,
    )
    app = create_app(settings=settings, runtime=ModelRuntime(), load_model_on_startup=True)
    with TestClient(app) as c:
        yield c
    reset_settings_cache()


def test_ready_reports_model(client: TestClient) -> None:
    resp = client.get("/ready")
    assert resp.status_code == 200
    body = resp.json()
    assert body["ready"] is True
    assert body["model_id"]


def test_metadata_contract(client: TestClient) -> None:
    resp = client.get("/v1/metadata", headers=auth_header(mint_token()))
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body["classes"], list) and len(body["classes"]) == 10
    assert body["input"]["dimensions"] == [32, 32]
    assert "low_confidence_threshold" in body["confidence_policy"]
    assert body["disclaimers"]


def test_predict_contract(client: TestClient) -> None:
    resp = client.post(
        "/v1/predict",
        files={"file": ("x.png", png_bytes(), "image/png")},
        headers=auth_header(mint_token()),
        params={"top_k": 3},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert 0 <= body["top1_class"] <= 9
    assert body["decision"] in {"accept", "low_confidence", "uncertain"}
    assert len(body["top_k"]) == 3
    assert body["request_id"]
    assert resp.headers.get("X-Request-Id")
