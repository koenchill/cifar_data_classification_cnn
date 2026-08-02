# Phase 06 — Production Training Controls and Experiment Tracking

| Field | Value |
|---|---|
| Release | B |
| Depends | Phase 5 |
| Status | `done` |
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

  - [x] Seed generators/workers; validate config; atomic full-state checkpoints; best/last/resume

### Tracking

  - [x] Human-readable + JSONL/CSV/TensorBoard; attach identities

### Authorization

  - [x] Restrict artifact writes; separate training/eval/release identities (policy)

## Deliverables

- `Checkpoint manager + resume path + tracking outputs`
- `Reproducibility report + access policy`
- `docs/evidence/release-b/phase-06-gate.md`

## Exit gate

- [x] Resume and best-model restoration tests pass
- [x] Two short seeded runs meet tolerance; unauthorized mutation denied

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

- [x] All workstream tasks complete
- [x] Deliverables exist at listed paths
- [x] Exit gate criteria satisfied
- [x] Verify commands recorded/pass
- [x] No global stop condition triggered
