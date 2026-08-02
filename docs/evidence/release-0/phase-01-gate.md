# Phase 01 Exit Gate

| Field | Value |
|---|---|
| Phase | 01 — Secure Repository, Developer Environment, and CI Trust |
| Date | 2026-08-01 |
| Result | `passed` with documented dependency exception CYB-07 |
| Approver | koenchill |

## Deliverables

| Deliverable | Present |
|---|---|
| `pyproject.toml` (torch/torchvision/matplotlib pinned) | Yes — torch 2.7.1, torchvision 0.22.1, matplotlib 3.9.4 |
| `requirements.lock` | Yes |
| `.pre-commit-config.yaml` | Yes |
| `.secrets.baseline` | Yes |
| `.github/CODEOWNERS` | Yes |
| `.github/workflows/ci-pr.yml` (SHA-pinned actions) | Yes |
| `docs/governance/secure_development_checklist.md` | Yes |
| `docs/governance/branch_protection.md` | Yes |
| `docs/governance/supply_chain_policy.md` (CycloneDX) | Yes |
| `docs/architecture/ci_oidc_trust.md` | Yes |

## Verify results

| Check | Result |
|---|---|
| Python 3.11 venv + `pip install -e ".[dev]"` | Pass |
| `import torch, torchvision, matplotlib` | Pass (`2.7.1+cpu`, `0.22.1+cpu`, `3.9.4`) |
| `ruff check` | Pass |
| `mypy` | Pass |
| `bandit -r src` | Pass (no issues) |
| `detect-secrets scan --baseline` | Pass |
| `pytest -q` | Pass (0 tests collected — expected pre–Phase 2) |
| `pre-commit run --all-files` | Pass |
| `pip-audit` | Executes; residual torch advisories → CYB-07 accepted to 2026-11-01 |
| PR CI cannot apply/deploy | Pass by design (`id-token: none`, `iam-negative-guard`) |

## Exit gate

- [x] Clean clone reproduces environment with guide libraries (Python **3.11** required; system 3.14 unsupported for this pin set)
- [x] Secret/SAST/dependency checks execute
- [x] Branch controls documented; CI short-lived scoped credentials design + PR negative guard
- [x] Negative IAM proof for PR CI: no OIDC apply token; fails if static AWS keys present; full AWS deny tests deferred to Phase 13 account bootstrap

## Exception

**CYB-07:** Remaining `torch==2.7.1` advisories tracked in risk register. Compensating controls: offline training threat model for Releases A–B; reassess before Release C image; upgrade when torchvision-compatible fixed releases available. Expiry 2026-11-01.

## Notes for operators

1. Enable GitHub branch protection per `docs/governance/branch_protection.md`.  
2. Create protected environments listed in `ci_oidc_trust.md` before Terraform apply workflows (Phase 13).  
3. Always create venv with `py -3.11 -m venv .venv` on this workstation.
