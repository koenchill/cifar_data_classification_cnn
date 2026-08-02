# Runbook — GitOps Rollback and Drift Repair

## Purpose

Roll back a bad promotion or repair cluster drift using **Git + Argo CD**, not CI cluster apply.

## Rollback (bad digest / unhealthy sync)

1. Identify the promotion commit that changed `deploy/kustomize/overlays/<env>/kustomization.yaml`.
2. Open a PR that **reverts the promotion** (`git revert <sha>` or restore the previous `digest:` line).
3. Merge after CI green (prod overlay changes still require normal branch protection / reviewers).
4. Argo self-heal reconciles pods to the prior digest; watch `cifar-cnn-<env>` until Healthy.
5. Do **not** `kubectl apply` or `kubectl set image` for routine rollback.

## Drift (manual cluster change)

1. Argo marks the Application **OutOfSync** when live state diverges from Git.
2. Prefer **self-heal** (enabled on all CIFAR-CNN apps) to restore Git desired state.
3. If a legitimate change is needed, edit the Kustomize overlay in Git and merge — never leave a permanent UI override.
4. Unauthorized override/exec/delete attempts are denied by AppProject + `argocd-rbac-cm` policies.

## Abort criteria

- Signature/digest admission rejects the image → stop; do not disable Kyverno Enforce.
- Sync loops fail after retry budget → page on-call; capture Application events; consider revert PR.
