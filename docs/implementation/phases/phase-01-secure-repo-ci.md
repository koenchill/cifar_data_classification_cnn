# Phase 01 — Secure Repository, Developer Environment, and CI Trust Foundation

| Field | Value |
|---|---|
| Release | 0 |
| Depends | Phase 0 |
| Status | `done` |
| Evidence | `docs/evidence/release-0/phase-01-gate.md` |

## Objective

Build a secure and reproducible development foundation, including the student-guide toolchain (`torch`, `torchvision`, `matplotlib`).

## Allowed paths

- `pyproject.toml`
- `.pre-commit-config.yaml`
- `.github/`
- `.gitignore`
- `Makefile`
- `docs/governance/`
- `docs/architecture/`
- `docs/evidence/release-0/`
- `README.md`
- `lockfile (uv.lock or equivalent)`

## Forbidden

- Full CIFAR-10 training in PR CI
- Long-lived AWS access keys in repo or secrets
- Unpinned GitHub Actions or base images
- Omitting guide-required libraries from baseline dependencies

## Workstreams

### Guide toolchain (§2)

  - [x] Document VS Code + Python as the local editor/runtime
  - [x] Declare runtime deps: `torch`, `torchvision`, `matplotlib`
  - [x] Provide reproducible install equivalent to `pip install torch torchvision matplotlib` (editable install + lock)
  - [x] Document local CPU default; optional GPU note (guide is CPU-oriented)

### Repository controls

  - [x] Document branch protection for main/release
  - [x] Require reviewed PRs, status checks, CODEOWNERS for security/infra/GitOps
  - [x] Prohibit direct production changes

### Developer environment

  - [x] Pin Python and tool versions in pyproject
  - [x] Add dependency lock and isolated venv instructions
  - [x] Add pre-commit: format, lint, typecheck, secret scan, lightweight SAST

### CI identity

  - [x] Design GitHub OIDC federation for cloud roles
  - [x] Separate build / terraform-plan / terraform-apply / gitops-update permissions

### Supply-chain policy

  - [x] Pin actions and base images by immutable reference
  - [x] Define dependency/base-image update cadence and vuln SLA
  - [x] Choose SPDX or CycloneDX SBOM

### CI architecture

  - [x] Fast PR checks use synthetic fixtures only
  - [x] Protected environment approval required for Terraform apply and prod GitOps

## Deliverables

- `pyproject.toml` + lock file (includes torch/torchvision/matplotlib)
- `.pre-commit-config.yaml`
- `.github/CODEOWNERS`
- `.github/workflows/ci-pr.yml`
- `docs/governance/secure_development_checklist.md`
- `docs/architecture/ci_oidc_trust.md`
- `docs/evidence/release-0/phase-01-gate.md`

## Exit gate

- [x] Clean clone reproduces environment with guide libraries importable
- [x] Secret/SAST/dependency/license checks execute
- [x] Branch controls documented; CI uses short-lived scoped credentials
- [x] Negative IAM tests prove build cannot apply infra or deploy directly

## Verify

```text
py -3.11 -m venv .venv
.\.venv\Scripts\python -m pip install -e ".[dev]"
python -c "import torch, torchvision, matplotlib; print(torch.__version__)"
pre-commit run --all-files
```

## Done when

- [x] All workstream tasks complete
- [x] Deliverables exist at listed paths
- [x] Exit gate criteria satisfied
- [x] Verify commands recorded/pass
- [x] No global stop condition triggered
