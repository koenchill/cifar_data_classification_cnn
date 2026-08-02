# Phase 11 — Secure FastAPI Service: OAuth/OIDC, RBAC, Limits, and Audit

| Field | Value |
|---|---|
| Release | C |
| Depends | Phase 10 |
| Status | `todo` |
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

  - [ ] OIDC validation: issuer, audience, signature, exp/nbf, scopes, key rotation

### Authorization

  - [ ] Scopes/roles for predict/metadata/health/admin; deny-by-default RBAC

### Input security

  - [ ] Content-type/magic bytes, size, dimensions, decompression, color modes, timeout, safe errors

### Abuse controls

  - [ ] Rate limits, quotas, concurrency, timeouts, top-k bounds, backpressure, 413/429

### Audit

  - [ ] Timestamp, correlation ID, subject, action, model/version, authz, security events, latency, status

### Secrets/config

  - [ ] Runtime secrets; validate env; redact logs; fail startup on invalid security settings

## Deliverables

- `/health /ready /v1/predict + metadata contract`
- `OIDC/RBAC middleware, rate limiter, audit schema, secure errors, tests`
- `docs/evidence/release-c/phase-11-gate.md`

## Exit gate

- [ ] OIDC/RBAC suites pass; malformed/oversized fail safely
- [ ] 401/403/413/429 stable; audit completeness/redaction pass

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

- [ ] All workstream tasks complete
- [ ] Deliverables exist at listed paths
- [ ] Exit gate criteria satisfied
- [ ] Verify commands recorded/pass
- [ ] No global stop condition triggered
