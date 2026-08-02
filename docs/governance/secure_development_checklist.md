# Secure Development Checklist

## Local environment

- [ ] Use **VS Code** (or compatible) + **Python 3.11**  
- [ ] Create isolated venv: `python -m venv .venv` then activate  
- [ ] Install: `python -m pip install -U pip && pip install -e ".[dev]"`  
  - CPU note: on Linux CI we use PyTorch CPU wheels via extra index; local default follows official torch wheels for your platform  
- [ ] Optional GPU: install CUDA-enabled torch builds separately; document device in run records (guide baseline is CPU-oriented)  
- [ ] `pre-commit install`  
- [ ] Never commit `.env`, keys, or `*.tfstate`

## Guide toolchain (§2)

| Library | Purpose | Declared |
|---|---|---|
| PyTorch (`torch`) | CNN | `pyproject.toml` |
| Torchvision | CIFAR-10 + transforms | `pyproject.toml` |
| Matplotlib | Visualization | `pyproject.toml` |

Equivalent to `pip install torch torchvision matplotlib` via editable install of this project.

## Before every PR

- [ ] Branch from latest `dev`: `git checkout -b feature/<phase>-<topic>`  
- [ ] `pre-commit run --all-files`  
- [ ] `pytest -q` (synthetic/unit; no full 10-epoch job in PR)  
- [ ] No secrets added  
- [ ] CODEOWNERS paths reviewed if touching infra/deploy/github/governance  
- [ ] PR title `type(scope): summary`; template fully completed  
- [ ] Follow `CONTRIBUTING.md` / `pr_best_practices.md`

## CI expectations

- Fast PR checks only (`ci-pr.yml`)  
- No full CIFAR-10 training in PR CI  
- No long-lived AWS keys  
- Actions pinned by SHA  

## Related docs

- `branch_protection.md`  
- `supply_chain_policy.md`  
- `../architecture/ci_oidc_trust.md`  
- `quality_release_policy.md`  
