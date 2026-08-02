# Penetration Test Tabletop — Phase 16

| Field | Value |
|---|---|
| Type | Adversarial tabletop (no live customer cluster) |
| Date | 2026-08-02 |
| Facilitator | Security owner |

## Attack paths exercised (paper + automated proxies)

| # | Scenario | Expected control | Automated proxy | Result |
|---|---|---|---|---|
| 1 | Anonymous `/v1/predict` in prod config | 401/403 | `tests/security/test_oidc_rbac.py` | Pass |
| 2 | Role without predict permission | Deny | RBAC tests | Pass |
| 3 | Oversized / bomb image | 413/422 | `test_input_limits.py` | Pass |
| 4 | Tampered bundle / bad HMAC | Fail closed | `test_bundle_tamper.py` | Pass |
| 5 | Mutable `:latest` in cifar-cnn ns | Admission deny | Kyverno policy tests | Pass (manifest) |
| 6 | CI holds AWS keys / applies prod | Forbidden | `iam-negative-guard`, gitops workflow asserts | Pass |
| 7 | Argo exec / override / delete | RBAC deny | `test_argocd_gitops.py` | Pass |

## Out of scope this RC

- Network pivoting on live EKS
- IdP token theft against real OIDC provider
- Physical / social engineering

## Disposition

Tabletop **pass** for desk RC. Full live pen test scheduled as Phase 17 ORR precondition when AWS/EKS exist (`DEF-16-01`).
