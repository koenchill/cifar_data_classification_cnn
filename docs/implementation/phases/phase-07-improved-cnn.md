# Phase 07 — Improved CNN, Augmentation, Batch Normalization, and Dropout

| Field | Value |
|---|---|
| Release | B |
| Depends | Phase 6 |
| Status | `done` |
| Evidence | `docs/evidence/release-b/phase-07-gate.md` |

## Objective

Evaluate controlled improvements without changing the guide baseline.

## Allowed paths

- `src/cifar_cnn/models/`
- `src/cifar_cnn/data/`
- `configs/`
- `tests/`
- `docs/evidence/release-b/`
- `docs/governance/risk_register.md`

## Forbidden

- Changing Phase 2-5 baseline guide path behavior
- Augmenting evaluation transforms

## Workstreams

### Model development

  - [x] Training-only crop/flip/optional color jitter; configurable BN and dropout

### Experimental quality

  - [x] Baseline vs aug-only vs reg-only vs combined ablations under same protocol/seeds

### AI risk

  - [x] Document benefit, failure modes, config changes, evidence, residual overfitting risk

## Deliverables

- `Improved model/configs; learning curves; ablation report; updated risk register`
- `docs/evidence/release-b/phase-07-gate.md`

## Exit gate

- [x] No evaluation transform is augmented; comparisons reproduce
- [x] Material regressions/uncertainty documented, not hidden

## Verify

```text
pytest -q tests/unit -k aug_train_only
```

## Cursor prompt (copy)

```text
Execute Phase 07 only per docs/implementation/phases/phase-07-improved-cnn.md.
Respect Allowed paths and Forbidden paths.
Complete workstreams in order; check off tasks as done.
Write exit-gate evidence to docs/evidence/release-b/phase-07-gate.md.
Do not start the next phase.
```

## Done when

- [x] All workstream tasks complete
- [x] Deliverables exist at listed paths
- [x] Exit gate criteria satisfied
- [x] Verify commands recorded/pass
- [x] No global stop condition triggered
