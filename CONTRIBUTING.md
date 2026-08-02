# Contributing / PR best practices

This repo uses **pull requests as the change-control boundary**. Do not push routine work straight to `main`. Prefer feature branches into `dev`.

## Branching model

```text
feature/<phase>-<short-topic>  →  PR  →  dev  →  PR  →  main
```

| Branch | Purpose |
|---|---|
| `main` | Protected; release-quality only |
| `dev` | Integration branch; accept phase/feature PRs |
| `feature/*` or `phase-NN-*` | Day-to-day work |
| `release/*` | Optional freeze lines (same protection as `main`) |

### Rules

1. **One concern per PR** — ideally one phase card, or a tightly related subset.
2. **No direct commits to `main`.** Direct commits to `dev` are discouraged; use a PR even for solo work so CI and the template run.
3. **Rebase or merge from `dev` before review** so CI reflects current integration.
4. **Do not bundle** guide-baseline changes with infra/GitOps/security refactors unless inseparable.
5. **Never commit secrets**, `.env`, tfstate, model weights, or raw CIFAR downloads.

## Before opening a PR

```bash
py -3.11 -m venv .venv   # if needed
# activate venv
pip install -e ".[dev]"
pre-commit install
pre-commit run --all-files
pytest -q
```

- Confirm the phase card **Allowed paths** were respected.
- Link the phase card and update `docs/implementation/STATUS.md` if the phase completes.
- Keep PR CI free of full CIFAR-10 training jobs.

## PR title

Use a short, imperative summary (≈ ≤72 chars):

```text
feat(phase-02): add CIFAR-10 data contract and split tests
fix(ci): pin actions by SHA and block AWS keys in PR CI
docs(governance): complete phase 00 exit gate
```

Prefixes: `feat`, `fix`, `docs`, `chore`, `ci`, `refactor`, `test`, `security`.

## PR body

The GitHub template is mandatory. Fill every section; delete only clearly N/A items and mark them `N/A`.

Include:

- **Why** (problem / phase exit gate), not only what  
- **How to test** (commands)  
- **Risk / rollback** for infra or model-affecting changes  
- Links to phase card + evidence paths when closing a gate  

## Review expectations

| Change touches | Reviewer focus |
|---|---|
| `src/cifar_cnn/data`, splits, guide baseline | Guide contract + leakage |
| `infra/`, `deploy/`, `.github/` | CODEOWNERS; least privilege; no secrets |
| Model/training | Repro, metrics honesty, intended-use claims |
| Docs/governance only | Claim language; RACI/risk consistency |

- Prefer **small diffs**; split if review would take > ~30 minutes.  
- Resolve conversations before merge.  
- Squash-merge is preferred for feature PRs into `dev` (clean history).  
- Merge commits OK for `dev` → `main` release PRs when preserving phase boundaries matters.

## Merge checklist (author)

- [ ] CI green: `lint-test`, `iam-negative-guard`  
- [ ] CODEOWNERS approval when required  
- [ ] No unresolved threads  
- [ ] Evidence/gate files updated if claiming a phase exit  
- [ ] Follow-ups filed (issues or STATUS notes), not hidden in the PR  

## What not to do

- Force-push to `main` / shared `dev` after others have based work on it  
- `--no-verify` to skip hooks without an explicit, documented reason  
- Expand PR scope mid-review (“while I’m here”)  
- Claim NIST certification or real-world safety from CIFAR accuracy  

See also: `docs/governance/branch_protection.md`, `docs/governance/pr_best_practices.md`, `docs/governance/secure_development_checklist.md`.
