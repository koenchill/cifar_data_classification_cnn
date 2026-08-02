# Phase 11 — Secure FastAPI Service: OAuth/OIDC, RBAC, Limits, and Audit

| Field | Value |
|---|---|
| Release | C |
| Depends | Phase 10 |
| Status | `done` |
| Evidence | `docs/evidence/release-c/phase-11-gate.md` |

## Objective

Implement enterprise-hardening requirements in the application boundary.

## Allowed paths

- `src/cifar_cnn/api/`
- `src/cifar_cnn/inference/`
- `configs/serve/`
- `tests/contract/`
- `tests/security/`
- `tests/e2e/`
- `docs/architecture/`
- `docs/evidence/release-c/`
- `.env.example`

## Forbidden

- Anonymous prediction unless explicitly risk-accepted
- Fetching arbitrary user URLs for inference
- Logging image bytes, tokens, or secrets

## Workstreams

### Authentication

  - [x] OIDC validation: issuer, audience, signature, exp/nbf, scopes, key rotation

### Authorization

  - [x] Scopes/roles for predict/metadata/health/admin; deny-by-default RBAC

### Input security

  - [x] Content-type/magic bytes, size, dimensions, decompression, color modes, timeout, safe errors

### Abuse controls

  - [x] Rate limits, quotas, concurrency, timeouts, top-k bounds, backpressure, 413/429

### Audit

  - [x] Timestamp, correlation ID, subject, action, model/version, authz, security events, latency, status

### Secrets/config

  - [x] Runtime secrets; validate env; redact logs; fail startup on invalid security settings

## Deliverables

- `/health /ready /v1/predict + metadata contract`
- `OIDC/RBAC middleware, rate limiter, audit schema, secure errors, tests`
- `docs/evidence/release-c/phase-11-gate.md`

## Exit gate

- [x] OIDC/RBAC suites pass; malformed/oversized fail safely
- [x] 401/403/413/429 stable; audit completeness/redaction pass

## Verify

```text
pytest -q tests/security tests/contract
```

## Cursor prompt (copy)

```text
Execute Phase 11 only per docs/implementation/phases/phase-11-secure-api.md.
Respect Allowed paths and Forbidden paths.
Complete workstreams in order; check off tasks as done.
Write exit-gate evidence to docs/evidence/release-c/phase-11-gate.md.
Do not start the next phase.
```

## Done when

- [x] All workstream tasks complete
- [x] Deliverables exist at listed paths
- [x] Exit gate criteria satisfied
- [x] Verify commands recorded/pass
- [x] No global stop condition triggered
