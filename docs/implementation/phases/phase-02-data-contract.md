# Phase 02 — CIFAR-10 Data Contract, Governance, and Leakage-Safe Splits

| Field | Value |
|---|---|
| Release | A |
| Depends | Phase 1 |
| Status | `done` |
| Evidence | `docs/evidence/release-a/phase-02-gate.md` |
| Guide steps | §3 Step 1 (+ class names for Step 6) |

## Objective

Implement the guide’s exact CIFAR-10 load/transform/DataLoader contract, then add lineage and leakage-safe splits without changing that baseline.

## Allowed paths

- `src/cifar_cnn/data/`
- `configs/data/`
- `tests/unit/`
- `tests/fixtures/`
- `data/splits/`
- `docs/governance/`
- `docs/model_cards/`
- `docs/evidence/release-a/`
- `docs/implementation/GUIDE_TRACEABILITY.md`

## Forbidden

- Mutating official test set for training/tuning
- Non-guide normalization or missing `ToTensor()` on baseline path
- Augmentation on evaluation/test transforms
- Changing batch size or shuffle flags for baseline loaders

## Workstreams

### Guide contract (Step 1) — exact

  - [x] `transforms.Compose([ToTensor(), Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])`
  - [x] `CIFAR10(root='./data' or project `data/`, train=True, download=True, transform=…)`
  - [x] `CIFAR10(..., train=False, download=True, transform=…)`
  - [x] Train `DataLoader`: `batch_size=32`, `shuffle=True`
  - [x] Test `DataLoader`: `batch_size=32`, `shuffle=False`
  - [x] Assert lengths: 50,000 train / 10,000 test
  - [x] Define official CIFAR-10 `classes` tuple

### Split integrity (additive)

  - [x] Deterministic stratified train/val indices from the 50k training set only
  - [x] Lock official test set until final evaluation
  - [x] Tests for disjointness and class distribution

### Provenance and security

  - [x] Record source/version/license/hashes/path/access/transform lineage
  - [x] Treat dataset/split changes as reviewed model-affecting changes

### AI RMF Map

  - [x] Document relevance, limitations, representativeness, class semantics
  - [x] Document CIFAR-10 vs enterprise imagery mismatch

## Deliverables

- `src/cifar_cnn/data/` modules + tests
- `configs/data/baseline.yaml` (guide loader flags)
- `docs/model_cards/data_card.md`
- `data/splits/split_manifest.json`
- Updated rows in `docs/implementation/GUIDE_TRACEABILITY.md`
- `docs/evidence/release-a/phase-02-gate.md`

## Exit gate

- [x] Guide Step 1 contract tests pass (transform, root, download, batch, shuffle, sizes)
- [x] Class-name constant available for visualization
- [x] Lineage reproducible; leakage checks pass
- [x] Limitations and prohibited inference claims approved

## Verify

```text
pytest -q tests/unit -k "data_contract or splits or classes or lineage"
```

## Done when

- [x] All workstream tasks complete
- [x] Deliverables exist at listed paths
- [x] Exit gate criteria satisfied
- [x] Verify commands recorded/pass
- [x] No global stop condition triggered
