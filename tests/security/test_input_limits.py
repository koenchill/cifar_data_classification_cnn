"""Input validation, size limits, and rate limiting."""

from __future__ import annotations

from fastapi.testclient import TestClient

from tests.security.helpers import auth_header, mint_token, png_bytes


def test_oversized_payload_413(client: TestClient) -> None:
    token = mint_token()
    # Valid PNG header but oversized body relative to max_upload_bytes=50_000
    huge = png_bytes() + (b"\x00" * 60_000)
    resp = client.post(
        "/v1/predict",
        files={"file": ("big.png", huge, "image/png")},
        headers=auth_header(token),
    )
    assert resp.status_code == 413
    assert resp.json()["detail"] == "payload_too_large"


def test_wrong_dimensions_400(client: TestClient) -> None:
    token = mint_token()
    resp = client.post(
        "/v1/predict",
        files={"file": ("x.png", png_bytes((64, 64)), "image/png")},
        headers=auth_header(token),
    )
    assert resp.status_code == 400
    assert resp.json()["detail"] == "invalid_dimensions"


def test_wrong_content_type_415(client: TestClient) -> None:
    token = mint_token()
    resp = client.post(
        "/v1/predict",
        files={"file": ("x.bin", b"not-an-image", "application/octet-stream")},
        headers=auth_header(token),
    )
    assert resp.status_code == 415


def test_magic_mismatch_400(client: TestClient) -> None:
    token = mint_token()
    resp = client.post(
        "/v1/predict",
        files={"file": ("x.png", b"notpngbutclaimed", "image/png")},
        headers=auth_header(token),
    )
    assert resp.status_code == 400
    assert resp.json()["detail"] == "invalid_image_magic"


def test_rate_limit_429(client: TestClient) -> None:
    token = mint_token(sub="rate-limited-user")
    headers = auth_header(token)
    files = {"file": ("x.png", png_bytes(), "image/png")}
    codes = []
    for _ in range(6):
        codes.append(client.post("/v1/predict", files=files, headers=headers).status_code)
    assert 429 in codes
    assert codes.count(200) == 5
