# Model Card Addendum — Rigorous Evaluation (Release B / Phase 08)

| Field | Value |
|---|---|
| Applies to | Guide `SimpleCNN` and additive `ImprovedCNN` candidates |
| Status | Measure evidence only — **non-production** |
| Official test | Locked for reporting; **not** used for tuning |

## Metrics (AI RMF Measure)

Beyond headline accuracy:

- Confusion matrix
- Per-class / macro / weighted precision, recall, F1
- Macro one-vs-rest ROC-AUC (when defined)
- Expected Calibration Error (ECE) on max-softmax confidence

Evidence: `docs/evidence/release-b/phase-08-metrics.json`, `phase-08-confusion.png`.

## Robustness (behavioral, not certified)

Smoke checks for blur, noise, wrong-size/mode rejection, NaN inputs, and OOD uniform noise.
**Do not** interpret pass/observed rows as adversarial robustness claims.

Evidence: `docs/evidence/release-b/phase-08-robustness.json`.

## Explainability

Grad-CAM on `conv3` for representative predicted/alternate-class overlays.
Limitation: localization aid only — not causal proof of reasoning.

Evidence: `phase-08-gradcam-*.png`.

## Safety / API confidence policy

Softmax confidence is **not** proof of correctness. Future API responses use:

| Decision | Rule (defaults) |
|---|---|
| `low_confidence` | top-1 prob `< 0.55` |
| `uncertain` | top-1 − top-2 margin `< 0.08` |
| `accept` | otherwise (still disclaimer-bearing) |

Evidence: `docs/evidence/release-b/phase-08-safety-policy.json`.
