# Phase 05 — Baseline Evaluation, Visualization, Persistence, and Learning Evidence

| Field | Value |
|---|---|
| Release | A |
| Depends | Phase 4 |
| Status | `todo` |
| Evidence | `docs/evidence/release-a/phase-05-gate.md` |
| Guide steps | §3 Steps 5–7; §1; §4; tough questions |

## Objective

Close **all** student-guide requirements and Release A with linked evidence (no gaps vs `GUIDE_TRACEABILITY.md`).

## Allowed paths

- `src/cifar_cnn/evaluation/`
- `scripts/`
- `models/`
- `cnn_model.pth` (repo-root guide path; gitignored)
- `artifacts/`
- `docs/model_cards/`
- `docs/evidence/release-a/`
- `docs/implementation/GUIDE_TRACEABILITY.md`
- `tests/`

## Forbidden

- Unsupported real-world performance or safety claims
- Using official test set for hyperparameter tuning
- Skipping Actual/Predicted class-name labels on the 8-image gallery
- Saving only a non-guide path without satisfying Step 7 compatibility

## Workstreams

### Evaluation (Step 5) — exact

  - [ ] `torch.no_grad()` over testloader
  - [ ] `_, predicted = torch.max(outputs, 1)`
  - [ ] Account for exactly **10,000** test predictions
  - [ ] Print/record: `Accuracy of the network on 10,000 test images: {pct}%`
  - [ ] Prefer `net.eval()` (additive)
  - [ ] Record loss as additive metric (optional; accuracy is mandatory)

### Visualization (Step 6) — exact + additive

  - [ ] Unnormalize with `img / 2 + 0.5` (equivalent to guide `imshow`)
  - [ ] Display/save **8** test images
  - [ ] Each title includes `Actual: {class}` and `Predicted: {class}` using official class names
  - [ ] Deterministic gallery artifact under `artifacts/` or `docs/evidence/release-a/`
  - [ ] Additive OK: confidence + correctness flags (do not replace Actual/Predicted)

### Persistence (Step 7) — exact path compatibility

  - [ ] `torch.save(net.state_dict(), …)`
  - [ ] Write `models/cnn_model.pth` (repo layout)
  - [ ] Also write repo-root `cnn_model.pth` **or** prove load-equivalence to guide path in tests
  - [ ] Verify load + inference in a clean process
  - [ ] Print/log “Model saved successfully!” (or equivalent evidence)

### Learning evidence (§1, §4, tough questions)

  - [ ] `learning_why_image_classification.md` covering guide §1
  - [ ] Short note covering guide §4 (DS importance / industries)
  - [ ] Answer all **20** tough questions from `guide_tough_questions_source.md` in `guide_questions.md`
  - [ ] Document baseline limitations and **non-production** status
  - [ ] Mark every row in `GUIDE_TRACEABILITY.md` complete with evidence links

## Deliverables

- Evaluation metrics file (accuracy on 10k; optional loss)
- 8-image gallery with Actual/Predicted labels
- `models/cnn_model.pth` and guide-compatible `cnn_model.pth` (or equivalence proof)
- Load/inference test
- `docs/model_cards/baseline_model_card.md`
- `docs/evidence/release-a/learning_why_image_classification.md`
- `docs/evidence/release-a/guide_questions.md`
- Completed `docs/implementation/GUIDE_TRACEABILITY.md`
- `docs/evidence/release-a/phase-05-gate.md`

## Exit gate

- [ ] Every `GUIDE_TRACEABILITY.md` requirement row is satisfied
- [ ] Steps 5–7 behaviors match the guide (plus documented additive fields only)
- [ ] All 20 tough questions answered in `guide_questions.md`
- [ ] No unsupported real-world performance/safety claim; Release A complete when matrix is green

## Verify

```text
pytest -q tests/integration -k "baseline_eval or gallery or model_save"
Test-Path docs/evidence/release-a/guide_questions.md
Test-Path docs/implementation/GUIDE_TRACEABILITY.md
```

## Cursor prompt (copy)

```text
Execute Phase 05 only per docs/implementation/phases/phase-05-baseline-evaluation.md.
Close every GUIDE_TRACEABILITY.md row for Steps 5–7 and §§1/4/questions.
Respect Allowed paths and Forbidden paths.
Write exit-gate evidence to docs/evidence/release-a/phase-05-gate.md.
Do not start the next phase.
```

## Done when

- [ ] All workstream tasks complete
- [ ] Deliverables exist at listed paths
- [ ] Exit gate criteria satisfied
- [ ] Verify commands recorded/pass
- [ ] No global stop condition triggered
