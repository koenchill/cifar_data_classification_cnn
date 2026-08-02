# Release and Rollback Package — Release E

## Release path (production)

1. Build/sign image via `ci-image` → digest `sha256:…`  
2. Stage: `gitops-promote` `target=staging` → merge → Argo `cifar-cnn-staging` Healthy  
3. Prod: `gitops-promote` `target=prod` with Environment **`gitops-prod`** approval → merge  
4. Argo `cifar-cnn-prod` reconciles digest-pinned Deployment (prune + self-heal)  
5. Kyverno Enforce: digest + cosign keyless  
6. Post-deploy smoke: `/health`, `/ready`, authenticated predict  

**Forbidden:** CI `kubectl apply` / helm upgrade to prod; mutable `:latest` desired state.

## Rollback path

1. Identify last known-good overlay digest (Git history).  
2. `git revert` promotion commit or restore prior `digest:` → PR → merge.  
3. Argo self-heal rolls pods to previous image.  
4. If bundle-level: restore prior bundle identity per model card ops; fail closed if HMAC invalid.  
5. Confirm alerts clear; write incident note if Sev-2+.

Refs: `docs/runbooks/gitops-rollback.md`, `docs/runbooks/continuity-restore.md`.

## Artifact set for this train

| Class | Location |
|---|---|
| Desired state | `deploy/kustomize/overlays/{dev,staging,prod}` |
| GitOps | `deploy/argocd/` |
| Image evidence | Phase 12 capacity + ci-image signatures |
| Model bundle cards | `docs/model_cards/` |
| Verification | Phase 16 `verification_results.json` |
