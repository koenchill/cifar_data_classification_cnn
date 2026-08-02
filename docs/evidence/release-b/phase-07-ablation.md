# Phase 07 Ablation Report

| Field | Value |
|---|---|
| Protocol | `configs/experiments/ablation_protocol.yaml` |
| Dataset | FakeCIFAR10 smoke (not a CIFAR-10 claim) |
| Eval augmentation | **false** (mandatory) |
| Curves JSON | `phase-07-learning_curves.json` |

## Arms (same seed/optimizer/epochs)

| Variant | Train aug | BN/Dropout | Final train loss | Final eval loss | Loss curve |
|---|---|---|---|---|---|
| baseline | False | False/False | 1.9775 | 1.6150 | [2.2015087604522705, 1.9774773915608723] |
| aug_only | True | False/False | 1.9775 | 1.6150 | [2.2015087604522705, 1.9774773915608723] |
| reg_only | False | True/True | 2.2244 | 2.2133 | [2.2392663955688477, 2.2244087060292563] |
| combined | True | True/True | 2.2247 | 2.2134 | [2.238044341405233, 2.2246593634287515] |

## Interpretation

- Smoke ablations confirm the **protocol is comparable and reproducible**, not that
  one arm is production-ready.
- Benefit hypothesis: aug + BN/Dropout should reduce overfitting on real CIFAR-10;
  FakeCIFAR constant images can invert or flatten rankings — do not hide that.
- Failure modes: heavier aug can underfit small nets; dropout can raise train loss
  while helping generalization; BN train/eval mode mismatch if `model.eval()` skipped.
- Residual: **AIR-03** overfitting / weak generalization remains medium until Phase 8–9
  rigor and champion selection on locked test with declared rules.

## Config changes vs guide baseline

| Item | Baseline (A) | Improved path (B) |
|---|---|---|
| Model | SimpleCNN | ImprovedCNN (optional BN/Dropout) |
| Train transform | guide ToTensor+Normalize | + RandomCrop/Flip (+ optional ColorJitter) |
| Eval/test transform | guide (no aug) | **unchanged guide / `build_eval_transform`** |
