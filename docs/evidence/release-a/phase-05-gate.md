# Phase 05 Exit Gate

| Field | Value |
|---|---|
| Phase | 05 — Baseline Evaluation, Visualization, Persistence, Learning Evidence |
| Date | 2026-08-01 |
| Result | `passed` |
| Approver | koenchill (model owner) |
| Release | **A closed** (GUIDE_TRACEABILITY matrix complete) |

## Deliverables

| Deliverable | Present |
|---|---|
| Eval metrics (10k accuracy) | `docs/evidence/release-a/baseline_metrics.json` |
| 8-image gallery Actual/Predicted | `docs/evidence/release-a/baseline_gallery.png` |
| Dual-path persistence | `save_baseline_model` → `models/cnn_model.pth` + `cnn_model.pth` |
| Model card | `docs/model_cards/baseline_model_card.md` |
| Learning §1/§4 | `learning_why_image_classification.md` |
| 20 tough questions | `guide_questions.md` |
| Traceability | `docs/implementation/GUIDE_TRACEABILITY.md` (all rows evidenced) |

## Verify

```text
pytest -q tests/integration -k "baseline_eval or gallery or model_save"
Test-Path docs/evidence/release-a/guide_questions.md
# True
```

Smoke CLI (FakeCIFAR10, full 10k eval):

```text
python scripts/evaluate.py --smoke --skip-save
# Accuracy of the network on 10000 test images: …
```

## Exit gate

- [x] Every GUIDE_TRACEABILITY.md requirement row satisfied
- [x] Steps 5–7 match guide (+ additive confidence/correctness on gallery; additive test loss)
- [x] All 20 tough questions answered
- [x] No unsupported real-world performance/safety claims; non-production documented

## Notes

- Smoke metrics use FakeCIFAR10 (constant images) so accuracy is not a CIFAR-10 claim.
- Live CIFAR-10 10-epoch train + eval remains offline: train then `python scripts/evaluate.py --checkpoint …`.
- Root `cnn_model.pth` is gitignored; equivalence proven in integration tests.
