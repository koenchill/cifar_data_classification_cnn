# Phase 08 — Rigorous Evaluation, Robustness, and Grad-CAM

| Field | Value |
|---|---|
| Release | B |
| Depends | Phases 6-7 |
| Status | `done` |
| Evidence | `docs/evidence/release-b/phase-08-gate.md` |

## Objective

Expand AI RMF Measure evidence beyond headline accuracy.

## Allowed paths

- `src/cifar_cnn/evaluation/`
- `scripts/`
- `tests/`
- `artifacts/`
- `docs/model_cards/`
- `docs/evidence/release-b/`

## Forbidden

- Using official test set for tuning
- Overstating adversarial robustness
- Treating softmax confidence as proof of correctness

## Workstreams

### Metrics

  - [x] Accuracy/loss; macro/weighted/per-class P/R/F1; confusion; ROC/AUC; calibration as selected

### Robustness

  - [x] Corrupted/blur/noise/wrong-size/wrong-mode/malformed/OOD/high-confidence unfamiliar inputs

### Explainability

  - [x] Grad-CAM for representative correct/incorrect cases with limitations

### Safety behavior

  - [x] Define when API returns low-confidence/uncertain flags

## Deliverables

- `Metrics/robustness report + plots; Grad-CAM galleries; model card update`
- `docs/evidence/release-b/phase-08-gate.md`

## Exit gate

- [x] Metric fixture tests pass; test set unused for tuning
- [x] Critical robustness failures owned/treated or residual-risk accepted

## Verify

```text
pytest -q tests/unit -k metrics_fixtures
```

## Cursor prompt (copy)

```text
Execute Phase 08 only per docs/implementation/phases/phase-08-rigorous-evaluation.md.
Respect Allowed paths and Forbidden paths.
Complete workstreams in order; check off tasks as done.
Write exit-gate evidence to docs/evidence/release-b/phase-08-gate.md.
Do not start the next phase.
```

## Done when

- [x] All workstream tasks complete
- [x] Deliverables exist at listed paths
- [x] Exit gate criteria satisfied
- [x] Verify commands recorded/pass
- [x] No global stop condition triggered
