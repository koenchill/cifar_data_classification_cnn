# Phase → path ownership

| Phase | Primary write paths |
|---|---|
| 0 | `docs/governance/`, `docs/architecture/`, `docs/evidence/release-0/` |
| 1 | `pyproject.toml`, `.pre-commit-config.yaml`, `.github/`, lockfile, governance checklists |
| 2 | `src/cifar_cnn/data/`, `configs/data/`, `data/splits/`, `tests/unit/`, data card |
| 3 | `src/cifar_cnn/models/`, `configs/model/`, model integrity tests |
| 4 | `src/cifar_cnn/training/`, `configs/train/`, `scripts/`, `artifacts/` |
| 5 | `src/cifar_cnn/evaluation/`, `models/`, gallery + guide Q evidence |
| 6 | training controls/checkpoints/tracking under `src/cifar_cnn/training/` |
| 7 | improved models + train-only aug; update risk register |
| 8 | evaluation metrics/robustness/Grad-CAM |
| 9 | transfer learning configs/checkpoints + champion decision |
| 10 | `src/cifar_cnn/inference/`, ONNX/bundle, AI release gate |
| 11 | `src/cifar_cnn/api/`, `configs/serve/`, security/contract tests |
| 12 | `deploy/docker/`, capacity evidence |
| 13 | `infra/terraform/` |
| 14 | `deploy/kustomize/`, runbooks/alerts |
| 15 | `deploy/argocd/`, promotion workflows |
| 16 | `tests/` consolidation + `docs/evidence/release-e/` |
| 17 | ORR docs, final acceptance, release package |
