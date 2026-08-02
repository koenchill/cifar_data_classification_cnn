# Phase 06 — Production Training Controls and Experiment Tracking

| Field | Value |
|---|---|
| Release | B |
| Depends | Phase 5 |
| Status | `todo` |
| Evidence | `docs/evidence/release-b/phase-06-gate.md` |

## Objective

Add typed config, determinism, resumable checkpoints, early stopping, scheduling, and tracking.

## Allowed paths

- `src/cifar_cnn/training/`
- `configs/train/`
- `scripts/`
- `tests/`
- `artifacts/`
- `docs/governance/`
- `docs/evidence/release-b/`

## Forbidden

- Weakening access controls on artifact write paths
- Non-atomic checkpoint writes as sole persistence

## Workstreams

### Controls

  - [ ] Seed generators/workers; validate config; atomic full-state checkpoints; best/last/resume

### Tracking

  - [ ] Human-readable + JSONL/CSV/TensorBoard; attach identities

### Authorization

  - [ ] Restrict artifact writes; separate training/eval/release identities (policy)

## Deliverables

- `Checkpoint manager + resume path + tracking outputs`
- `Reproducibility report + access policy`
- `docs/evidence/release-b/phase-06-gate.md`

## Exit gate

- [ ] Resume and best-model restoration tests pass
- [ ] Two short seeded runs meet tolerance; unauthorized mutation denied

## Verify

```text
pytest -q tests -k "checkpoint_resume or seeded_runs"
```

## Cursor prompt (copy)

```text
Execute Phase 06 only per docs/implementation/phases/phase-06-training-controls.md.
Respect Allowed paths and Forbidden paths.
Complete workstreams in order; check off tasks as done.
Write exit-gate evidence to docs/evidence/release-b/phase-06-gate.md.
Do not start the next phase.
```

## Done when

- [ ] All workstream tasks complete
- [ ] Deliverables exist at listed paths
- [ ] Exit gate criteria satisfied
- [ ] Verify commands recorded/pass
- [ ] No global stop condition triggered
