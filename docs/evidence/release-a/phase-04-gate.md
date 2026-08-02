# Phase 04 Exit Gate

| Field | Value |
|---|---|
| Phase | 04 — Correct Guide Baseline Training |
| Date | 2026-08-01 |
| Result | `passed` |
| Approver | koenchill (model owner) |

## Deliverables

| Deliverable | Present |
|---|---|
| `src/cifar_cnn/training/trainer.py` | Yes |
| `scripts/train.py` | Yes |
| `configs/train/baseline.yaml` | Yes (epochs=10, lr=0.001, Adam, CrossEntropy) |
| Unit tests | `tests/unit/test_trainer.py` |
| Smoke run record | `docs/evidence/release-a/phase-04-smoke-run.json` |

## Guide defect note

Student guide Step 4 prints `running_loss / 100` every 100 mini-batches but never
executes `running_loss += loss.item()`. The baseline trainer accumulates each batch
loss before averaging and resetting. Documented in `run_record.json` under
`guide_defect_note`.

## Verify

```text
pytest -q tests/unit -k "trainer_step or running_loss"
# 2 passed
python scripts/train.py --config configs/train/baseline.yaml --smoke
# elapsed ~0.05s CPU; checkpoint + run_record under artifacts/baseline_smoke/
```

## Full 10-epoch plan (compute-limited)

PR CI and this gate use `--smoke` (synthetic TensorDataset, 1 epoch, few batches).
Full guide baseline (CIFAR-10, 10 epochs, CPU) is offline:

```text
python scripts/train.py --config configs/train/baseline.yaml
```

Artifacts land in `artifacts/baseline/` (gitignored). Reproducibility fields in the
run record: config, seed, device, env versions, loss_history, epoch timings.

## Exit gate

- [x] Unit optimizer-step test matches guide step order
- [x] Corrected running-loss accumulation verified
- [x] Smoke run reproducible from config; full-run plan documented
- [x] Resource use does not exhaust selected environment

## Security

Training writes trusted `state_dict` checkpoints via `save_state_dict` (same Phase 3
integrity path). No secrets in run records.
