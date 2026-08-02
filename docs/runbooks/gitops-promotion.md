# Runbook — GitOps Digest Promotion

## Purpose

Promote a signed, digest-pinned API image through environments using **Git as the only desired-state store**. Argo CD reconciles the cluster; CI never `kubectl apply`s.

## Preconditions

- Image built and cosign-signed by `ci-image` (digest known).
- Kyverno policies `cifar-cnn-require-image-digest` and `cifar-cnn-verify-signed-images` Enforce in the target cluster.
- GitHub Environment `gitops-prod` configured with required reviewers (prod only).

## Staging (auto after merge)

1. In Actions, run **gitops-promote** with `target=staging` and `digest=sha256:…`.
2. Workflow opens a PR updating `deploy/kustomize/overlays/staging` (and aligned `dev`).
3. Merge when PR CI is green.
4. Confirm Argo Application `cifar-cnn-staging` → Synced/Healthy (prune + self-heal on).

Optional: set `dry_run=true` to validate overlay edits without opening a PR.

## Production (approved)

1. Run **gitops-promote** with `target=prod` and the same (or verified) digest.
2. Approve the GitHub Environment **`gitops-prod`** gate.
3. Review/merge the PR that touches only `deploy/kustomize/overlays/prod`.
4. Confirm Argo Application `cifar-cnn-prod` → Synced/Healthy.
5. Smoke `/health` and authenticated `/v1/predict` per ops checklist.

## Forbidden

- CI or humans applying production manifests with cluster-admin outside break-glass.
- Promoting `:latest` or unsigned digests.
- Argo UI **override** / **exec** / application **delete** (RBAC denies for operator roles).
