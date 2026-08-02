# Phase 09 — Transfer Learning and Champion Selection

| Field | Value |
|---|---|
| Release | B |
| Depends | Phase 8 |
| Status | `done` |
| Evidence | `docs/evidence/release-b/phase-09-gate.md` |

## Objective

Compare ResNet18 with SimpleCNN variants under a predeclared selection rule.

## Allowed paths

- `src/cifar_cnn/models/`
- `configs/model/`
- `configs/train/`
- `scripts/`
- `tests/`
- `docs/model_cards/`
- `docs/evidence/release-b/`

## Forbidden

- Selecting champion using official test set
- Skipping licensing/supply-chain documentation for pretrained weights

## Workstreams

### Transfer path

  - [x] Document weights, preprocessing, classifier replacement, freeze/finetune, license, provenance

### Comparison

  - [x] Val macro-F1/acc, robustness, calibration, latency, size, memory, cost, interpretability, security/ops

### Selection

  - [x] Freeze candidate before official-test evaluation; model-owner and AI-risk review

## Deliverables

- `ResNet config/checkpoint; fair comparison; champion decision + rejected alternatives`
- `docs/evidence/release-b/phase-09-gate.md`

## Exit gate

- [x] Selection follows declared criteria without test leakage
- [x] Champion footprint fits envelope or capacity revised

## Verify

```text
pytest -q tests/integration -k champion_selection
```

## Cursor prompt (copy)

```text
Execute Phase 09 only per docs/implementation/phases/phase-09-transfer-champion.md.
Respect Allowed paths and Forbidden paths.
Complete workstreams in order; check off tasks as done.
Write exit-gate evidence to docs/evidence/release-b/phase-09-gate.md.
Do not start the next phase.
```

## Done when

- [x] All workstream tasks complete
- [x] Deliverables exist at listed paths
- [x] Exit gate criteria satisfied
- [x] Verify commands recorded/pass
- [x] No global stop condition triggered
