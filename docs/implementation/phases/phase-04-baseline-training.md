# Phase 04 — Correct Guide Baseline Training

| Field | Value |
|---|---|
| Release | A |
| Depends | Phase 3 |
| Status | `done` |
| Evidence | `docs/evidence/release-a/phase-04-gate.md` |
| Guide steps | §3 Steps 3–4 |

## Objective

Train with the guide’s `CrossEntropyLoss`, `Adam(lr=0.001)`, 10 epochs, and **corrected** mini-batch loss reporting.

## Allowed paths

- `src/cifar_cnn/training/`
- `scripts/`
- `configs/train/`
- `tests/unit/`
- `tests/integration/`
- `artifacts/`
- `docs/evidence/release-a/`
- `docs/implementation/GUIDE_TRACEABILITY.md`

## Forbidden

- Changing guide hyperparams for the baseline path (`lr`, epochs, loss, optimizer family)
- Colocating full training with inference Kubernetes deployment
- Printing loss without accumulating `loss.item()` (replicating the guide bug)

## Workstreams

### Loss and optimizer (Step 3) — exact

  - [x] `criterion = nn.CrossEntropyLoss()`
  - [x] `optimizer = optim.Adam(net.parameters(), lr=0.001)`

### Training loop (Step 4) — exact + bugfix

  - [x] `for epoch in range(10):`
  - [x] Per batch: unpack `(inputs, labels)` → `optimizer.zero_grad()` → `outputs = net(inputs)` → `loss = criterion(outputs, labels)` → `loss.backward()` → `optimizer.step()`
  - [x] **Guide bug fix:** `running_loss += loss.item()` every batch
  - [x] When `i % 100 == 99`: print epoch/batch/avg loss (`running_loss / 100`), then reset `running_loss = 0.0`
  - [x] Document the guide defect in evidence (missing accumulation in snippet)
  - [x] Prefer `net.train()` during training (additive; guide-implied)

### Reproducibility (additive)

  - [x] Capture config, seed, env, code version, dataset/split IDs, device, timings, hashes
  - [x] Default device CPU (guide); optional GPU profile recorded separately

### Compute

  - [x] CPU training benchmark; optional single GPU profile

## Deliverables

- Trainer + CLI (`scripts/train.py` or package entry)
- `configs/train/baseline.yaml` (epochs=10, lr=0.001, Adam, CrossEntropy)
- Baseline run record + loss histories + checkpoints under `artifacts/`
- Note on guide loss-print defect
- Updated `GUIDE_TRACEABILITY.md` Steps 3–4
- `docs/evidence/release-a/phase-04-gate.md`

## Exit gate

- [x] Unit optimizer-step test matches guide step order
- [x] Corrected running-loss accumulation verified
- [x] Ten-epoch run reproducible from its record (or smoke + documented full-run plan if compute-limited)
- [x] Resource use does not exhaust selected environment

## Verify

```text
pytest -q tests/unit -k "trainer_step or running_loss"
python scripts/train.py --config configs/train/baseline.yaml --smoke
```

## Cursor prompt (copy)

```text
Execute Phase 04 only per docs/implementation/phases/phase-04-baseline-training.md.
Match GUIDE_TRACEABILITY.md Steps 3–4; fix the running_loss accumulation bug.
Respect Allowed paths and Forbidden paths.
Write exit-gate evidence to docs/evidence/release-a/phase-04-gate.md.
Do not start the next phase.
```

## Done when

- [x] All workstream tasks complete
- [x] Deliverables exist at listed paths
- [x] Exit gate criteria satisfied
- [x] Verify commands recorded/pass
- [x] No global stop condition triggered
