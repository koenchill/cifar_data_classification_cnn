# Phase 03 — Guide-Exact SimpleCNN and Model Integrity

| Field | Value |
|---|---|
| Release | A |
| Depends | Phase 2 |
| Status | `done` |
| Evidence | `docs/evidence/release-a/phase-03-gate.md` |
| Guide steps | §3 Step 2 |

## Objective

Implement the guide’s exact `SimpleCNN` (no advanced substitutions) and prove integrity with tests.

## Allowed paths

- `src/cifar_cnn/models/`
- `configs/model/`
- `tests/unit/`
- `docs/model_cards/`
- `docs/evidence/release-a/`
- `docs/implementation/GUIDE_TRACEABILITY.md`

## Forbidden

- BatchNorm / Dropout / ResNet / extra convs in baseline `SimpleCNN`
- Changing kernel size, padding, channels, or FC dims
- Arbitrary pickle/object deserialization for model load

## Workstreams

### Model (Step 2) — exact layer contract

  - [x] `self.conv1 = nn.Conv2d(3, 32, 3, padding=1)`
  - [x] `self.pool = nn.MaxPool2d(2, 2)` (shared)
  - [x] `self.conv2 = nn.Conv2d(32, 64, 3, padding=1)`
  - [x] `self.conv3 = nn.Conv2d(64, 64, 3, padding=1)`
  - [x] `self.fc1 = nn.Linear(64 * 4 * 4, 64)`  # 1024 → 64
  - [x] `self.fc2 = nn.Linear(64, 10)`
  - [x] Forward exactly (logits, no softmax)

### Integrity

  - [x] Shape test: input `(N,3,32,32)` → output `(N,10)`
  - [x] Gradient finite; parameter-count documented (122,570)
  - [x] Serialization round trip; config compatibility; malformed-shape fail closed

### Security

  - [x] Document trusted artifact formats; load only verified/application-generated bundles

## Deliverables

- `src/cifar_cnn/models/simple_cnn.py`
- `configs/model/simple_cnn.yaml`
- `docs/model_cards/simplecnn_summary.md`
- Updated `GUIDE_TRACEABILITY.md` Step 2 rows
- `docs/evidence/release-a/phase-03-gate.md`

## Exit gate

- [x] Layer constructors and forward match guide snippet line-for-line in behavior
- [x] Forward/backward finite; shapes and param counts match
- [x] Serialization round trip passes; tampered artifacts fail closed

## Verify

```text
pytest -q tests/unit -k simple_cnn
```

## Done when

- [x] All workstream tasks complete
- [x] Deliverables exist at listed paths
- [x] Exit gate criteria satisfied
- [x] Verify commands recorded/pass
- [x] No global stop condition triggered
