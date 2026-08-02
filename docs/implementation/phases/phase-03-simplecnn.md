# Phase 03 — Guide-Exact SimpleCNN and Model Integrity

| Field | Value |
|---|---|
| Release | A |
| Depends | Phase 2 |
| Status | `todo` |
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

  - [ ] `self.conv1 = nn.Conv2d(3, 32, 3, padding=1)`
  - [ ] `self.pool = nn.MaxPool2d(2, 2)` (shared)
  - [ ] `self.conv2 = nn.Conv2d(32, 64, 3, padding=1)`
  - [ ] `self.conv3 = nn.Conv2d(64, 64, 3, padding=1)`
  - [ ] `self.fc1 = nn.Linear(64 * 4 * 4, 64)`  # 1024 → 64
  - [ ] `self.fc2 = nn.Linear(64, 10)`
  - [ ] Forward exactly:
        `x = pool(relu(conv1(x)))`
        `x = pool(relu(conv2(x)))`
        `x = pool(relu(conv3(x)))`
        `x = x.view(-1, 64 * 4 * 4)`
        `x = relu(fc1(x))`
        `x = fc2(x)` → return logits (no softmax)

### Integrity

  - [ ] Shape test: input `(N,3,32,32)` → output `(N,10)`
  - [ ] Gradient finite; parameter-count documented
  - [ ] Serialization round trip; config compatibility; malformed-shape fail closed

### Security

  - [ ] Document trusted artifact formats; load only verified/application-generated bundles

## Deliverables

- `src/cifar_cnn/models/simple_cnn.py`
- `configs/model/simple_cnn.yaml`
- `docs/model_cards/simplecnn_summary.md`
- Updated `GUIDE_TRACEABILITY.md` Step 2 rows
- `docs/evidence/release-a/phase-03-gate.md`

## Exit gate

- [ ] Layer constructors and forward match guide snippet line-for-line in behavior
- [ ] Forward/backward finite; shapes and param counts match
- [ ] Serialization round trip passes; tampered artifacts fail closed

## Verify

```text
pytest -q tests/unit -k simple_cnn
```

## Cursor prompt (copy)

```text
Execute Phase 03 only per docs/implementation/phases/phase-03-simplecnn.md.
Match GUIDE_TRACEABILITY.md Step 2 rows exactly (channels, kernel=3, padding=1, FC dims).
Respect Allowed paths and Forbidden paths.
Write exit-gate evidence to docs/evidence/release-a/phase-03-gate.md.
Do not start the next phase.
```

## Done when

- [ ] All workstream tasks complete
- [ ] Deliverables exist at listed paths
- [ ] Exit gate criteria satisfied
- [ ] Verify commands recorded/pass
- [ ] No global stop condition triggered
