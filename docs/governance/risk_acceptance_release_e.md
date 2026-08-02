# Formal Residual Risk Acceptance — Release E

| Field | Value |
|---|---|
| Date | 2026-08-02 |
| Authority | AI system owner + Security owner + Final release approver (`koenchill`) |
| Scope | Desk-complete enterprise release package; first live traffic still requires environment bootstrap checklist |

## Accepted residuals

| ID | Summary | Compensating controls | Expiry / review |
|---|---|---|---|
| AIR-01 | Over-trust of CIFAR accuracy on real photos | Intended-use + model cards; prohibited uses; no safety claims | Review 2026-11-01 |
| AIR-05 | High-confidence OOD errors | OIDC/RBAC; confidence flags; no anonymous prod predict | Review 2026-11-01 |
| CYB-07 | Torch/torchvision advisories on pinned pair | Pin + Trivy; offline threat limited; upgrade track | **2026-11-01** |
| DEF-16-01 | No live customer-account EKS soak yet | Policy tests, runbooks, tabletops; **prod traffic blocked until bootstrap checklist** | Cleared when live ORR soak signed |
| DEF-16-02 | Non-gating deprecation warnings in pytest | Track upstream | Next dependency train |

## Explicit refusals

- Unsigned residual-risk acceptance: **forbidden** (this document is the signed record).  
- Production promotion outside Argo from immutable signed digest: **forbidden**.  
- NIST / FedRAMP certification claims: **not made**.

## Signatures (portfolio single-owner)

| Role | Decision | Date |
|---|---|---|
| AI system owner | Accept AIR-* with controls above | 2026-08-02 |
| Security owner | Accept CYB-07 + platform residuals with controls | 2026-08-02 |
| Final release approver | Accept package for Release E close | 2026-08-02 |
