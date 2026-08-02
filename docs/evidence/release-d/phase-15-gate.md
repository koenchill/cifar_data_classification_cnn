# Phase 15 Gate — Argo CD GitOps and Release D Close

| Field | Value |
|---|---|
| Phase | 15 — Argo CD / promotion / drift control |
| Release | D |
| Date | 2026-08-01 |
| Status | Pass (desired-state + policy tests; live Argo SSO deferred to cluster bootstrap) |

## Exit criteria

- [x] Desired-state isolation (AppProject sourceRepos + overlay paths); digest pinning in overlays
- [x] OIDC SSO ConfigMap values; AppProject/RBAC deny exec, override, delete
- [x] CI proposes digest PRs; staging auto after merge; prod via `gitops-prod` approval
- [x] Prune + self-heal on Applications; Kyverno digest + signed-image admission Enforce
- [x] Promotion dry-run evidence; rollback/drift runbooks; unauthorized actions denied in policy tests
- [x] Release D complete (`docs/evidence/release-d/release-d-decision.md`)

## Deliverables

| Artifact | Path |
|---|---|
| AppProject / Applications | `deploy/argocd/` |
| Admission policies | `deploy/argocd/policies/` |
| Promotion workflow | `.github/workflows/gitops-promote.yml` |
| Runbooks | `docs/runbooks/gitops-*.md` |
| Tests | `tests/integration/test_argocd_gitops.py` |
| Dry-run evidence | `docs/evidence/release-d/phase-15-promotion-dry-run.md` |

## Verify

```text
kubectl kustomize deploy/argocd
pytest -q tests/integration -k argocd_gitops
```

Local result (2026-08-01): **9 passed** (`tests/integration -k argocd_gitops`).

## Notes

- Bootstrap once with `deploy/argocd/root/app-of-apps.yaml` after Argo CD install; do not grant CI cluster-admin for routine sync.
- Replace placeholder IdP URL/client IDs via External Secrets at install time.
