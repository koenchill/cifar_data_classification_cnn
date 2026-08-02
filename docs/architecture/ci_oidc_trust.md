# CI Identity and OIDC Trust Design

## Principle

CI uses **GitHub OIDC federation** for cloud access. **No long-lived AWS access keys** in GitHub secrets for routine build/plan/apply/deploy.

## Role catalog (least privilege)

| Role | Trusted subjects (examples) | Permissions (intent) | Can apply infra? | Can deploy prod? |
|---|---|---|---|---|
| `ci-build` | `repo:ORG/REPO:ref:refs/heads/dev` and PRs | Push to non-prod ECR; read; sign attestations | **No** | **No** |
| `ci-terraform-plan` | workflow `terraform-plan.yml` on PR | `terraform plan` + read state | **No** | **No** |
| `ci-terraform-apply` | workflow on protected env `terraform-apply` | Apply to matching env only | **Yes (scoped)** | N/A |
| `ci-gitops-update` | workflow proposing digest PRs | Open PRs / limited write to desired-state paths | **No** | **No** (Argo reconciles) |

Production apply/promote requires **GitHub Environment protection rules** (required reviewers).

## PR CI (`ci-pr.yml`) trust posture

| Permission | Value | Rationale |
|---|---|---|
| `contents` | `read` | Checkout only |
| `id-token` | `none` | Cannot federate to AWS apply roles |
| AWS static keys | Forbidden | Negative guard fails job if present |

## Negative IAM tests (proof plan)

Until AWS accounts exist, proof is **design + workflow assertions**. When accounts exist, automate:

1. Assume `ci-build` → `terraform apply` must deny.  
2. Assume `ci-build` → `eks:UpdateClusterConfig` / `kubectl` admin must deny.  
3. Assume `ci-terraform-plan` → `terraform apply` must deny.  
4. PR workflow job env must not contain `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY`.  
5. `ci-pr` must not request `id-token: write`.

Current automated control: job `iam-negative-guard` in `.github/workflows/ci-pr.yml`.

## Protected environments (to configure in GitHub)

| Environment | Approvals | Used by |
|---|---|---|
| `terraform-apply-staging` | 1 reviewer | Terraform apply staging |
| `terraform-apply-prod` | 1+ reviewers | Terraform apply prod |
| `gitops-prod` | 1+ reviewers | Production digest promotion PR merge / sync trigger |

## Explicit non-goals for Phase 1

- Creating live AWS IAM roles (Phase 13)  
- Running Terraform from this phase  

Phase 1 delivers the **trust design** and **PR CI that cannot apply or deploy**.
