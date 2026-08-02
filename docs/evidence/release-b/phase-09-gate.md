# Phase 09 Exit Gate

| Field | Value |
|---|---|
| Phase | 09 — Transfer Learning and Champion Selection |
| Date | 2026-08-01 |
| Result | `passed` |
| Approver | koenchill (model owner) |

## Deliverables

| Deliverable | Present |
|---|---|
| ResNet18 transfer stack | `src/cifar_cnn/models/resnet_transfer.py`, configs, model card |
| Selection rule (val-only) | `champion.py` + `configs/model/champion_selection.yaml` |
| Comparison + decision | `phase-09-comparison.json`, `phase-09-champion-decision.json`, `phase-09-decision.md` |
| Integration tests | `tests/integration/test_champion_selection.py` |

## Verify

```text
pytest -q tests/integration -k champion_selection
python scripts/select_champion.py
```

## Exit gate

- [x] Selection follows declared criteria without test leakage
- [x] Champion footprint checked against envelope (reject or revise capacity)
- [x] Pretrained weight licensing/provenance documented

## Notes

CI uses `pretrained=false`. Offline IMAGENET1K_V1 fine-tune is opt-in via
`configs/train/transfer.yaml`.
