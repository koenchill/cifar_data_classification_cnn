# Phase 11 Gate — Secure FastAPI Service

| Field | Value |
|---|---|
| Phase | 11 — Secure FastAPI |
| Release | C |
| Date | 2026-08-01 |
| Status | Pass (local verify) |

## Exit criteria

- [x] OIDC validation (issuer/audience/exp/signature) and deny-by-default RBAC
- [x] Malformed / oversized / wrong-type inputs fail safely (400/413/415)
- [x] Stable 401 / 403 / 413 / 429 responses
- [x] Audit events include subject/action/model/status/request_id; redaction of tokens/bytes
- [x] Production config fails closed (no static OIDC; no anon predict)

## Deliverables

| Artifact | Path |
|---|---|
| API package | `src/cifar_cnn/api/` |
| Preprocess helper | `src/cifar_cnn/inference/preprocess.py` |
| Serve configs | `configs/serve/api.dev.yaml`, `configs/serve/api.prod.yaml` |
| Security tests | `tests/security/` |
| Contract tests | `tests/contract/` |
| E2E smoke | `tests/e2e/test_predict_smoke.py` |
| Architecture note | `docs/architecture/api_security.md` |
| Env template | `.env.example` |

## Verify

```text
pytest -q tests/security tests/contract
```

Local verify (2026-08-01): `21 passed` in `tests/security` + `tests/contract`; e2e smoke also green (`22` with `tests/e2e`).

## Risk notes

- AIR-05: production API now behind OIDC/RBAC + confidence flags; OOD high-confidence remains a residual model risk, not an open anonymous surface.
- Static HS256 OIDC mode is **dev/CI only**; production requires JWKS mode.
