# Release D Decision — Platform and GitOps Foundation

| Field | Value |
|---|---|
| Release | D (Terraform → K8s runtime → Argo CD) |
| Date | 2026-08-01 |
| Decision | **Accept** — proceed to Release E verification/ops phases |

## Scope closed

| Phase | Outcome |
|---|---|
| 13 Terraform / EKS foundation | Pass — modules, env stacks, plan-only CI, no static AWS keys |
| 14 Hardened K8s runtime | Pass — PSS, NetPol, HA/capacity, observability hooks, policy tests |
| 15 Argo CD GitOps | Pass — AppProjects/Apps, digest promotion, admission, drift/rollback |

## Residual risks (accepted for now)

- Live AWS apply / EKS bootstrap not yet executed in a customer account.
- Argo OIDC IdP endpoints are placeholders until enterprise SSO is wired.
- Image digests in overlays still use the local Phase-12 evidence digest until GHCR signed digests replace them via `gitops-promote`.

## Explicit non-claims

- Not a production go-live.
- Not a claim of NIST certification or FedRAMP authorization.

## Next

Release E starts at Phase 16 (Verification / QA) when scheduled.
