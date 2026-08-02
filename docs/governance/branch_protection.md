# Branch Protection and Change Control

## Branching model

```text
feature/<phase>-<topic>  →  PR (CI + template)  →  dev  →  PR  →  main
```

Routine implementation lands through **PRs into `dev`**. Promote integrated work `dev` → `main` with a release PR. See `CONTRIBUTING.md` and `pr_best_practices.md`.

## Protected branches

| Branch | Protection |
|---|---|
| `main` | Protected; no direct commits; PR + review + status checks required |
| `dev` | PR required for changes; status checks required; avoid direct push |
| `release/*` | Same as `main` when created |

## Required controls (enable in GitHub settings)

1. Require a pull request before merging  
2. Require at least 1 approving review (or admin solo-ack while single-owner; still use PR + CI)  
3. Require review from CODEOWNERS for `/infra`, `/deploy`, `/.github`, governance docs  
4. Require status checks (enabled on `dev` and `main`): `lint-test`, `iam-negative-guard` (`ci-pr.yml`); `title` (`pr-title.yml`); `sast`, `sca`, `dast` (`ci-security.yml`)  
5. Require conversation resolution before merge  
6. Restrict who can push to matching branches (admins optional bypass only for break-glass)  
7. **Prohibit direct production changes** — production desired state updates only via reviewed PR + Argo promotion (Phase 15), never `kubectl apply` from laptops as routine path  
8. Prefer **squash merge** for feature → `dev`; allow merge commits for `dev` → `main` when retaining phase boundaries

## Production change prohibition

- Application/infra production applies are not performed from PR CI.  
- Terraform apply and prod GitOps promotion use **protected GitHub Environments** with required reviewers (see `ci_oidc_trust.md`).  
- Unsigned or tag-only images are not admissible in production desired state.

## Break-glass

Documented, time-bounded, security-owner approved, with post-incident review. Not for routine delivery.
