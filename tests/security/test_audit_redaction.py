"""Audit completeness and redaction of secrets/bytes."""

from __future__ import annotations

import json

from fastapi.testclient import TestClient

from cifar_cnn.api.audit import get_audit_sink
from tests.security.helpers import auth_header, mint_token, png_bytes


def test_audit_records_predict_without_token_or_bytes(client: TestClient) -> None:
    token = mint_token(sub="auditor")
    resp = client.post(
        "/v1/predict",
        files={"file": ("x.png", png_bytes(), "image/png")},
        headers=auth_header(token),
    )
    assert resp.status_code == 200
    events = get_audit_sink().events
    predict_events = [e for e in events if e.action == "predict" and e.outcome == "success"]
    assert predict_events
    event = predict_events[-1]
    assert event.subject == "auditor"
    assert event.byte_length is not None and event.byte_length > 0
    assert event.content_type == "image/png"
    assert event.request_id
    assert event.model_id
    public = event.to_public_dict()
    dumped = json.dumps(public)
    assert token not in dumped
    assert "Authorization" not in dumped
    assert "\\x89PNG" not in dumped
    assert "image" not in public or public.get("content_type") == "image/png"


def test_denied_auth_is_audited(client: TestClient) -> None:
    client.post(
        "/v1/predict",
        files={"file": ("x.png", png_bytes(), "image/png")},
    )
    denied = [e for e in get_audit_sink().events if e.detail == "missing_bearer_token"]
    assert denied
    assert denied[-1].status_code == 401


def test_error_body_has_request_id_no_stack(client: TestClient) -> None:
    resp = client.post(
        "/v1/predict",
        files={"file": ("x.png", png_bytes((8, 8)), "image/png")},
        headers=auth_header(mint_token()),
    )
    assert resp.status_code == 400
    body = resp.json()
    assert "request_id" in body
    assert "Traceback" not in resp.text
    assert "File " not in resp.text
