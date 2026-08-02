# Pull Request Best Practices (Project Norms)

Companion to root `CONTRIBUTING.md`. These norms are part of Release 0 change control.

## Size and scope

| Prefer | Avoid |
|---|---|
| One phase card or one vertical slice | Multi-release megapacks |
| ≤ ~400 LOC meaningful diff when practical | Unrelated refactors in the same PR |
| Explicit “out of scope” notes | Silent scope creep past Allowed paths |

If a phase is large (e.g. Phase 11 API), split into stacked PRs (`phase-11a-routes`, `phase-11b-oidc`) that still merge via `dev`.

## CI contract for PRs

PR CI (`ci-pr.yml`) must remain:

- Fast and deterministic  
- Free of full CIFAR-10 training  
- Unable to Terraform-apply or deploy (`id-token: none`, no static AWS keys)

Fail the PR if those invariants regress.

## Security review triggers (request explicit security pass)

- Authn/authz, crypto, or audit logging changes  
- Dockerfile / Kustomize / Terraform  
- Dependency or Action pin changes  
- Anything that weakens rate limits, RBAC, or secret handling  

## Guide-baseline PRs (Phases 2–5)

Must cite `docs/implementation/GUIDE_TRACEABILITY.md` rows touched and include tests that lock guide behavior.

## Approval matrix (solo-owner today)

| Target | Minimum |
|---|---|
| `feature/*` → `dev` | CI green; self-review against template; CODEOWNERS paths acknowledged |
| `dev` → `main` | CI green; release notes / phase STATUS; no open Critical risks for the claimed release |

When a second human reviewer exists, require their approval on `main` and on `/infra` `/deploy` `/.github`.

## GitHub settings to enable (manual)

Documented in `branch_protection.md`. Until enabled in the UI, treat this file as the **policy source of truth** and follow it socially.
