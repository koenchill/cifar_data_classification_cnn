# Phase 02 — CIFAR-10 Data Contract, Governance, and Leakage-Safe Splits

| Field | Value |
|---|---|
| Release | A |
| Depends | Phase 1 |
| Status | `todo` |
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

  - [ ] `transforms.Compose([ToTensor(), Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])`
  - [ ] `CIFAR10(root='./data' or project `data/`, train=True, download=True, transform=…)`
  - [ ] `CIFAR10(..., train=False, download=True, transform=…)`
  - [ ] Train `DataLoader`: `batch_size=32`, `shuffle=True`
  - [ ] Test `DataLoader`: `batch_size=32`, `shuffle=False`
  - [ ] Assert lengths: 50,000 train / 10,000 test
  - [ ] Define official CIFAR-10 `classes` tuple (guide uses undefined `classes`):
        `airplane, automobile, bird, cat, deer, dog, frog, horse, ship, truck`

### Split integrity (additive)

  - [ ] Deterministic stratified train/val indices from the 50k training set only
  - [ ] Lock official test set until final evaluation
  - [ ] Tests for disjointness and class distribution

### Provenance and security

  - [ ] Record source/version/license/hashes/path/access/transform lineage
  - [ ] Treat dataset/split changes as reviewed model-affecting changes

### AI RMF Map

  - [ ] Document relevance, limitations, representativeness, class semantics
  - [ ] Document CIFAR-10 vs enterprise imagery mismatch

## Deliverables

- `src/cifar_cnn/data/` modules + tests
- `configs/data/baseline.yaml` (guide loader flags)
- `docs/model_cards/data_card.md`
- `data/splits/split_manifest.json`
- Updated rows in `docs/implementation/GUIDE_TRACEABILITY.md`
- `docs/evidence/release-a/phase-02-gate.md`

## Exit gate

- [ ] Guide Step 1 contract tests pass (transform, root, download, batch, shuffle, sizes)
- [ ] Class-name constant available for visualization
- [ ] Lineage reproducible; leakage checks pass
- [ ] Limitations and prohibited inference claims approved

## Verify

```text
pytest -q tests/unit -k "data_contract or splits or classes"
```

## Cursor prompt (copy)

```text
Execute Phase 02 only per docs/implementation/phases/phase-02-data-contract.md.
Match GUIDE_TRACEABILITY.md Step 1 rows exactly.
Respect Allowed paths and Forbidden paths.
Write exit-gate evidence to docs/evidence/release-a/phase-02-gate.md.
Do not start the next phase.
```

## Done when

- [ ] All workstream tasks complete
- [ ] Deliverables exist at listed paths
- [ ] Exit gate criteria satisfied
- [ ] Verify commands recorded/pass
- [ ] No global stop condition triggered
