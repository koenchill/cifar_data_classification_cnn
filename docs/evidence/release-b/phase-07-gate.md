# Phase 07 Exit Gate

| Field | Value |
|---|---|
| Phase | 07 — Improved CNN, Augmentation, BN, Dropout |
| Date | 2026-08-01 |
| Result | `passed` |
| Approver | koenchill (model owner) |

## Deliverables

| Deliverable | Present |
|---|---|
| ImprovedCNN | `src/cifar_cnn/models/improved_cnn.py` |
| Train-only aug transforms | `build_train_augment_transform` / `build_eval_transform` |
| Configs | `configs/model/improved_cnn.yaml`, `configs/data/train_augment.yaml`, `configs/experiments/ablation_protocol.yaml` |
| Ablation report + curves | `phase-07-ablation.md`, `phase-07-learning_curves.json` |
| Risk register | AIR-03 updated (treating) |
| Tests | `tests/unit/test_aug_train_only.py` |

## Verify

```text
pytest -q tests/unit -k aug_train_only
```

## Exit gate

- [x] No evaluation transform is augmented; comparisons reproduce under fixed seed
- [x] Material uncertainty documented (FakeCIFAR smoke ≠ CIFAR-10 claim; AIR-03 residual)

## Notes

Guide baseline SimpleCNN + guide transforms remain the Release A path. ImprovedCNN and
train aug are additive only.
