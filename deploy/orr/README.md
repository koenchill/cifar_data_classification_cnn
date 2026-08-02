# Deploy ORR pointers

Operational readiness artifacts for Release E live in docs; this folder marks the deploy tree as subject to ORR controls.

| Topic | Canonical doc |
|---|---|
| Promote / rollback | `docs/runbooks/gitops-promotion.md`, `gitops-rollback.md` |
| Alerts / SLOs | `docs/governance/slo_policy.md`, `../kustomize/base/prometheusrule.yaml` |
| Prod rule | Argo CD reconciles digest-pinned overlays only — never CI `kubectl apply` |

Bootstrap: `docs/evidence/release-e/orr_package.md`.
