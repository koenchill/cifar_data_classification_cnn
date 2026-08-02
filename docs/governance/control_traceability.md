# Control Traceability — Release E

Maps mandatory enterprise controls to evidence. Not a certification claim.

| Control | Source policy | Implementation | Verification |
|---|---|---|---|
| No secrets in source | supply_chain / quality | pre-commit + detect-secrets | ci-pr secret scan |
| Fail-closed security config | quality committed controls | API config | `tests/security/test_config_fail_closed.py` |
| Authentication + OIDC | quality | FastAPI OIDC/JWT | `tests/security/test_oidc_rbac.py` |
| RBAC deny-by-default | quality | RBAC module | security suites |
| Rate limiting | quality | rate limiter | `test_input_limits.py` / security |
| Audit without secrets/pixels | quality | audit module | `test_audit_redaction.py` |
| Signed digest images only (prod) | supply_chain / GitOps | overlays + Kyverno | `test_argocd_gitops.py` |
| CI no cluster-admin apply | ci_oidc_trust | permissions + gitops-promote | iam-negative-guard |
| Prod promote via Argo only | GitOps forbidden list | Applications + AppProject | phase-15 gate |
| Network default-deny + PSS | platform | Kustomize | `test_k8s_policy.py` |
| Terraform no static AWS keys | platform | terraform.yml OIDC | `tests/terraform/*` |
| Intended use / AI limits | intended_use / AI RMF | cards + register | Phase 16 AI review |
| SLOs + alerts | slo_policy | PrometheusRule + ConfigMap | alert-response runbook |
| Incident / vuln / continuity | ORR runbooks | docs/runbooks/* | alert_restore_tabletop |
| Residual risk acceptance | risk_register | signed acceptances | `risk_acceptance_release_e.md` |
