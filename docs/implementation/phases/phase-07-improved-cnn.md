# Phase 07 — Improved CNN, Augmentation, Batch Normalization, and Dropout

| Field | Value |
|---|---|
| Release | B |
| Depends | Phase 6 |
| Status | `todo` |
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

  - [ ] Training-only crop/flip/optional color jitter; configurable BN and dropout

### Experimental quality

  - [ ] Baseline vs aug-only vs reg-only vs combined ablations under same protocol/seeds

### AI risk

  - [ ] Document benefit, failure modes, config changes, evidence, residual overfitting risk

## Deliverables

- `Improved model/configs; learning curves; ablation report; updated risk register`
- `docs/evidence/release-b/phase-07-gate.md`

## Exit gate

- [ ] No evaluation transform is augmented; comparisons reproduce
- [ ] Material regressions/uncertainty documented, not hidden

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

- [ ] All workstream tasks complete
- [ ] Deliverables exist at listed paths
- [ ] Exit gate criteria satisfied
- [ ] Verify commands recorded/pass
- [ ] No global stop condition triggered
