# Phase 02 Exit Gate

| Field | Value |
|---|---|
| Phase | 02 — CIFAR-10 Data Contract & Leakage-Safe Splits |
| Date | 2026-08-01 |
| Result | `passed` |
| Approver | koenchill (data owner) |

## Deliverables

| Deliverable | Present |
|---|---|
| `src/cifar_cnn/data/` modules | Yes |
| `configs/data/baseline.yaml` | Yes |
| `docs/model_cards/data_card.md` | Yes |
| `data/splits/split_manifest.json` | Yes (seed=42, val_fraction=0.1) |
| GUIDE_TRACEABILITY Step 1 rows | Updated |

## Verify

```text
pytest -q tests/unit -k "data_contract or splits or classes or lineage"
# 12 passed, 1 skipped (live CIFAR optional unless CIFAR_CNN_LIVE_DATA=1 or cache present)
```

## Exit gate

- [x] Guide Step 1 contract tests pass (transform, root, download flags, batch, shuffle, sizes)
- [x] `CIFAR10_CLASSES` available for visualization
- [x] Lineage record reproducible; leakage/disjointness checks pass
- [x] Limitations and prohibited inference claims approved in data card

## Notes

- Unit tests use a FakeCIFAR10 stand-in so PR CI does not depend on slow torchvision downloads.
- Live size check runs when `./data/cifar-10-batches-py` exists or `CIFAR_CNN_LIVE_DATA=1`.
- Official test set remains locked; stratified val indices come only from the 50k training pool.
