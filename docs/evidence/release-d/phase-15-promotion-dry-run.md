# Phase 15 — Promotion Dry-Run Evidence

| Field | Value |
|---|---|
| Date | 2026-08-01 |
| Workflow | `.github/workflows/gitops-promote.yml` |
| Script | `deploy/argocd/scripts/propose_digest_promotion.py` |

## Dry-run procedure (local)

```text
python deploy/argocd/scripts/propose_digest_promotion.py \
  --digest sha256:0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef \
  --env staging
git diff -- deploy/kustomize/overlays/staging/kustomization.yaml
git checkout -- deploy/kustomize/overlays/staging/kustomization.yaml
```

## Observed (2026-08-01)

- Script rewrites only the pinned `digest:` field under the GHCR API image block.
- No `kubectl` / AWS credentials required for the proposal step.
- Prod path is gated by GitHub Environment `gitops-prod` in the workflow (approval before PR open).
- Staging Application syncPolicy: `automated.prune=true`, `automated.selfHeal=true`.
- Unauthorized Argo actions (`exec`, `override`, `delete`) denied in AppProject roles + global RBAC CSV.

## Trace checklist

| Step | Staging | Prod |
|---|---|---|
| CI proposes digest PR | Yes (`target=staging`) | Yes (`target=prod` + `gitops-prod`) |
| Human/CI cluster apply | No | No |
| Argo reconciles after merge | Auto | Auto after approved Git change |
| Admission (digest + cosign) | Enforce | Enforce |
| Rollback | Revert PR → Argo heal | Revert PR → Argo heal |
