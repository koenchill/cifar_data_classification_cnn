# Release C Decision Record

| Field | Value |
|---|---|
| Release | C — Secure API + hardened Docker envelope |
| Date | 2026-08-01 |
| Decision | **Approve** for local/demo Docker path and authenticated API boundary |
| Approver | koenchill |

## Scope approved

1. Phase 11 secure FastAPI (OIDC/RBAC/limits/audit/input security)
2. Phase 12 digest-pinned multi-stage image, scan/SBOM/sign workflow, capacity envelope

## Explicit non-claims

- Not NIST certified
- Local Docker **≠** EKS reference architecture
- Softmax confidence is not correctness proof
- Torch residual advisories remain under **CYB-07** (expiry 2026-11-01)

## Promotion rules

- Images promoted **by digest** only
- Production must use `CIFAR_CNN_OIDC_MODE=jwks` with issuer/audience/JWKS URL
- Anonymous predict forbidden in production

## Next

Release D starts at Phase 13 (Terraform / EKS platform).
