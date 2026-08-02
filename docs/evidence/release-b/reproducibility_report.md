# Reproducibility Report — Phase 06

| Field | Value |
|---|---|
| Date | 2026-08-01 |
| Config | `configs/train/controlled.yaml` |
| Seeds | Python `random` + `torch.manual_seed`; cudnn deterministic when enabled |
| Workers | `worker_init_fn` for DataLoader workers |
| Checkpoints | Atomic full-state (`model`, `optimizer`, `scheduler`, RNG, epoch, best_metric) |

## Seeded-run tolerance

Two short CPU smoke runs with identical `ControlledTrainConfig.seed` must match
`val_loss` history within absolute tolerance `1e-5` (see
`test_seeded_runs_match_within_tolerance`).

## Tracking identities

Each metrics JSONL/CSV row attaches `run_id`, `identity`, `model`, and `git_sha`
(when available). Human-readable log: `train.log`. TensorBoard SummaryWriter is
used when the `tensorboard` package is installed; otherwise scalars mirror to
`tensorboard/scalars.jsonl`.

## Access policy

See `docs/governance/artifact_access_policy.md`. Unauthorized writes (e.g. training
identity → `models/`) raise `ArtifactWriteDenied`.
