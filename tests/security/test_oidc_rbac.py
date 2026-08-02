"""OIDC validation and deny-by-default RBAC."""

from __future__ import annotations

from fastapi.testclient import TestClient

from tests.security.helpers import auth_header, mint_token, png_bytes


def test_predict_requires_bearer(client: TestClient) -> None:
    resp = client.post(
        "/v1/predict",
        files={"file": ("x.png", png_bytes(), "image/png")},
    )
    assert resp.status_code == 401
    assert resp.json()["detail"] == "missing_bearer_token"


def test_predict_rejects_expired_token(client: TestClient) -> None:
    token = mint_token(exp_delta=-10)
    resp = client.post(
        "/v1/predict",
        files={"file": ("x.png", png_bytes(), "image/png")},
        headers=auth_header(token),
    )
    assert resp.status_code == 401
    assert resp.json()["detail"] == "token_expired"


def test_predict_rejects_wrong_audience(client: TestClient) -> None:
    token = mint_token(audience="other-api")
    resp = client.post(
        "/v1/predict",
        files={"file": ("x.png", png_bytes(), "image/png")},
        headers=auth_header(token),
    )
    assert resp.status_code == 401
    assert resp.json()["detail"] == "invalid_token"


def test_predict_forbidden_without_scope(client: TestClient) -> None:
    token = mint_token(scopes="metadata:read")
    resp = client.post(
        "/v1/predict",
        files={"file": ("x.png", png_bytes(), "image/png")},
        headers=auth_header(token),
    )
    assert resp.status_code == 403
    assert resp.json()["detail"] == "insufficient_scope"


def test_metadata_forbidden_without_scope(client: TestClient) -> None:
    token = mint_token(scopes="predict:invoke")
    resp = client.get("/v1/metadata", headers=auth_header(token))
    assert resp.status_code == 403


def test_role_predictor_grants_predict(client: TestClient) -> None:
    token = mint_token(scopes="", roles=["predictor"])
    resp = client.post(
        "/v1/predict",
        files={"file": ("x.png", png_bytes(), "image/png")},
        headers=auth_header(token),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "top1_class" in body
    assert "decision" in body
    assert "disclaimers" in body


def test_health_is_public(client: TestClient) -> None:
    assert client.get("/health").status_code == 200
    assert client.get("/health").json()["status"] == "ok"
