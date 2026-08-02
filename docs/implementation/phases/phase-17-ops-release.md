# Phase 17 — Operational Readiness, AI RMF Manage, and Enterprise Release

| Field | Value |
|---|---|
| Release | E |
| Depends | Phase 16 |
| Status | `todo` |
| Evidence | `docs/evidence/release-e/phase-17-gate.md` |

## Objective

Prove operable, recoverable, patchable release under accountable control.

## Allowed paths

- `docs/runbooks/`
- `docs/governance/`
- `docs/model_cards/`
- `docs/evidence/release-e/`
- `deploy/`
- `infra/terraform/`

## Forbidden

- Production promotion outside Argo CD from immutable signed digest
- Unsigned residual-risk acceptance

## Workstreams

### ORR package

  - [ ] Runbooks; SLOs/alerts; IR exercises; vuln lifecycle; continuity; AI RMF Manage confirmation

## Deliverables

- `ORR package; final cards; control traceability; approved risk acceptance; release+rollback package`
- `docs/evidence/release-e/phase-17-gate.md`

## Exit gate

- [ ] Owners sign release decision; rollback/restore and critical alerts proven
- [ ] Residual risks accepted by named authority; prod via Argo signed digest only
- [ ] Release E complete

## Verify

```text
Test-Path docs/evidence/release-e/phase-17-gate.md
```

## Cursor prompt (copy)

```text
Execute Phase 17 only per docs/implementation/phases/phase-17-ops-release.md.
Respect Allowed paths and Forbidden paths.
Complete workstreams in order; check off tasks as done.
Write exit-gate evidence to docs/evidence/release-e/phase-17-gate.md.
Do not start the next phase.
```

## Done when

- [ ] All workstream tasks complete
- [ ] Deliverables exist at listed paths
- [ ] Exit gate criteria satisfied
- [ ] Verify commands recorded/pass
- [ ] No global stop condition triggered
