# Phase 15 — Argo CD GitOps, Environment Promotion, and Drift Control

| Field | Value |
|---|---|
| Release | D |
| Depends | Phase 14 |
| Status | `todo` |
| Evidence | `docs/evidence/release-d/phase-15-gate.md` |

## Objective

Make Git the desired-state source and Argo CD the only routine reconciler.

## Allowed paths

- `deploy/argocd/`
- `deploy/kustomize/`
- `.github/workflows/`
- `docs/runbooks/`
- `docs/evidence/release-d/`
- `tests/`

## Forbidden

- CI holding cluster-admin or directly applying production manifests
- Unsigned/tag-only images in production desired state

## Workstreams

### Repo model + Argo security

  - [ ] Desired-state isolation; digest pinning; OIDC SSO; AppProjects; deny exec/override/delete

### Promotion + reconciliation + admission

  - [ ] CI proposes digest; staging auto; prod approved; prune/self-heal; signed-image admission

## Deliverables

- `Argo apps/projects; promotion workflow; admission policies; drift/rollback tests`
- `docs/evidence/release-d/phase-15-gate.md`

## Exit gate

- [ ] Promotion traces complete; unauthorized actions denied; rollback succeeds
- [ ] Release D complete

## Verify

```text
Document promotion dry-run evidence under docs/evidence/release-d/
```

## Cursor prompt (copy)

```text
Execute Phase 15 only per docs/implementation/phases/phase-15-argocd-gitops.md.
Respect Allowed paths and Forbidden paths.
Complete workstreams in order; check off tasks as done.
Write exit-gate evidence to docs/evidence/release-d/phase-15-gate.md.
Do not start the next phase.
```

## Done when

- [ ] All workstream tasks complete
- [ ] Deliverables exist at listed paths
- [ ] Exit gate criteria satisfied
- [ ] Verify commands recorded/pass
- [ ] No global stop condition triggered
