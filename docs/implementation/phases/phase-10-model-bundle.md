# Phase 10 — Governed Model Bundle, ONNX, and AI Release Gate

| Field | Value |
|---|---|
| Release | B |
| Depends | Phase 9 |
| Status | `done` |
| Evidence | `docs/evidence/release-b/phase-10-gate.md` |

## Objective

Produce a portable, self-describing, integrity-protected release candidate.

## Allowed paths

- `src/cifar_cnn/inference/`
- `scripts/`
- `models/`
- `artifacts/`
- `docs/model_cards/`
- `docs/governance/`
- `docs/evidence/release-b/`
- `tests/`

## Forbidden

- Promoting high unresolved AI risks
- Unsigned/unhashed bundles into release evidence

## Workstreams

### Export

  - [x] ONNX with documented opset/names/dynamic batch; PyTorch parity

### Bundle

  - [x] Model, metadata, class order, normalization, constraints, metrics, limitations, identities

### Integrity

  - [x] Hash/sign bundle; tamper + rollback tests

### AI RMF gate

  - [x] Review Govern/Map/Measure; assign Manage actions, monitors, thresholds, rollback, retirement

## Deliverables

- `ONNX + parity report; versioned bundle; signed manifest; AI release decision`
- `docs/evidence/release-b/phase-10-gate.md`

## Exit gate

- [x] Load/dynamic-batch/parity/metadata/signature/tamper/rollback tests pass
- [x] High unresolved AI risks block promotion; Release B complete

## Verify

```text
pytest -q tests -k "onnx_parity or bundle_tamper"
```

## Cursor prompt (copy)

```text
Execute Phase 10 only per docs/implementation/phases/phase-10-model-bundle.md.
Respect Allowed paths and Forbidden paths.
Complete workstreams in order; check off tasks as done.
Write exit-gate evidence to docs/evidence/release-b/phase-10-gate.md.
Do not start the next phase.
```

## Done when

- [x] All workstream tasks complete
- [x] Deliverables exist at listed paths
- [x] Exit gate criteria satisfied
- [x] Verify commands recorded/pass
- [x] No global stop condition triggered
