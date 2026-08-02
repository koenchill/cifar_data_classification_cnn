# Artifact Access Policy (Training / Eval / Release)

**Status:** Active for Release B+ training controls  
**Control:** Deny by default; fail closed on unauthorized writes

## Identities

| Identity | Purpose | Allowed write roots |
|---|---|---|
| `training` | Model fitting, checkpoints, run metrics | `artifacts/` |
| `eval` | Evaluation metrics and evidence copies | `artifacts/`, `docs/evidence/` |
| `release` | Promoted model artifacts only | `models/`, `artifacts/release/` |

## Rules

1. Writes outside the workspace root are denied.
2. Path traversal (`..`) is denied.
3. Code and VCS trees (`src/`, `tests/`, `.git/`, `.github/`) are never writable via training APIs.
4. Checkpoint persistence must use atomic temp + replace (see `CheckpointManager`).
5. Training identity must not mutate release-promoted paths under `models/` (promotion is a separate `release` identity step).
6. Human operators use the same identity boundaries in CI jobs and local scripts (`--identity` / config field).

## Enforcement

Implemented in `cifar_cnn.training.authz.assert_artifact_write_allowed` and invoked before checkpoint/tracker writes.
