"""End-to-end smoke: authenticated predict against a packed test bundle."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from cifar_cnn.api.app import create_app
from cifar_cnn.api.config import Settings, reset_settings_cache
from cifar_cnn.api.runtime import ModelRuntime
from cifar_cnn.inference.bundle import pack_bundle
from cifar_cnn.models.simple_cnn import SimpleCNN
from tests.security.helpers import AUDIENCE, ISSUER, SECRET, auth_header, mint_token, png_bytes


@pytest.fixture
def client(tmp_path: Path) -> Iterator[TestClient]:
    reset_settings_cache()
    bundle = tmp_path / "e2e-bundle"
    pack_bundle(
        SimpleCNN(),
        bundle,
        bundle_id="e2e",
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
        rate_limit_per_minute=60,
        predict_timeout_sec=10.0,
        top_k_max=5,
        require_auth_for_ready=False,
    )
    with TestClient(
        create_app(settings=settings, runtime=ModelRuntime(), load_model_on_startup=True)
    ) as c:
        yield c
    reset_settings_cache()


def test_e2e_predict_smoke(client: TestClient) -> None:
    assert client.get("/ready").json()["ready"] is True
    resp = client.post(
        "/v1/predict",
        files={"file": ("smoke.png", png_bytes(), "image/png")},
        headers=auth_header(mint_token(roles=["predictor"])),
    )
    assert resp.status_code == 200
    assert "top1_class_name" in resp.json()
