# CIFAR-10 Data Classification CNN

Enterprise-ready CIFAR-10 CNN project: guide-compliant ML baseline first, then production ML assurance, secure FastAPI delivery, AWS/EKS + GitOps, and operational readiness.

## Repository layout (app-root gold standard)

```text
.
├── src/cifar_cnn/          # Installable package (src layout)
│   ├── data/               # Loaders, splits, transforms
│   ├── models/             # SimpleCNN, improved CNN, transfer models
│   ├── training/           # Train loops, checkpoints, tracking
│   ├── evaluation/         # Metrics, robustness, Grad-CAM
│   ├── inference/          # Predict / ONNX runtime helpers
│   ├── api/                # FastAPI service boundary
│   └── utils/              # Shared helpers (logging, seeds, IO)
├── configs/                # Typed YAML/TOML configs by concern
├── scripts/                # Thin CLIs (train, evaluate, export)
├── tests/                  # unit | integration | contract | security | e2e
├── notebooks/              # Exploration only (never production path)
├── data/                   # Local datasets + split manifests (raw ignored)
├── models/                 # Guide path: models/cnn_model.pth (weights ignored)
├── artifacts/              # Local run outputs / evidence (ignored)
├── docs/
│   ├── governance/         # AI RMF, RACI, risk, Zero Trust
│   ├── architecture/       # System context, threat model
│   ├── model_cards/        # Baseline / champion cards
│   ├── runbooks/           # Ops / incident / rollback
│   ├── evidence/           # Release evidence packs
│   └── implementation/     # Cursor-executable phase plan
├── deploy/
│   ├── docker/             # Hardened image definition
│   ├── kustomize/          # K8s base + env overlays
│   └── argocd/             # AppProjects / Applications
├── infra/terraform/        # Bootstrap + env stacks / modules
├── .github/                # Workflows, CODEOWNERS, templates
└── .cursor/rules/          # Agent structure + phase execution rules
```

## Local setup (Phase 1)

Editor/runtime: **VS Code** + **Python 3.11** (guide §2). Training default is **CPU**; optional GPU builds are documented per run, not required for the guide baseline.

```bash
# Prefer Python 3.11 (required). On Windows: py -3.11 -m venv .venv
python3.11 -m venv .venv
# Windows: .venv\Scripts\activate
# Unix: source .venv/bin/activate
python -m pip install -U pip
pip install -e ".[dev]"
pre-commit install
python -c "import torch, torchvision, matplotlib; print(torch.__version__)"
```

Pinned dependencies live in `pyproject.toml`; freeze with `make lock` → `requirements.lock`.

## Student guide (Release A)

Baseline ML must match the course guide exactly. Traceability matrix:

- [`docs/implementation/GUIDE_TRACEABILITY.md`](docs/implementation/GUIDE_TRACEABILITY.md)
- Source text: [`docs/evidence/release-a/student_guide.md`](docs/evidence/release-a/student_guide.md)

## How to execute phases with Cursor

1. Open [`docs/implementation/CURSOR_EXECUTION_PLAN.md`](docs/implementation/CURSOR_EXECUTION_PLAN.md).
2. Run **one phase at a time** from `docs/implementation/phases/`.
3. For Phases 1–5, close every applicable row in `GUIDE_TRACEABILITY.md`.
4. Do not start a phase until its **Depends** and prior **Exit gate** are satisfied.
5. Attach evidence under `docs/evidence/release-*` as listed on the phase card.
6. Land work via PR best practices in [`CONTRIBUTING.md`](CONTRIBUTING.md) (`feature/*` → `dev` → `main`).

## Deployment paths

| Path | When |
|---|---|
| Hardened Docker on one host | Local demo / portfolio / early integration |
| AWS EKS + Terraform + Argo CD | Full enterprise reference (default plan path) |

## Status

- Branch: `dev`
- Current execution target: **Phase 2** (data contract) — Phases 0–1 complete
- Claims policy: document as *mapped to selected NIST AI RMF outcomes* — never “NIST certified”
