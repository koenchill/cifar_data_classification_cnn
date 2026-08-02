# Phase 13 Gate — Terraform Cloud Foundation (EKS)

| Field | Value |
|---|---|
| Phase | 13 — Terraform network/IAM/EKS |
| Release | D |
| Date | 2026-08-01 |
| Status | Pass (fmt/validate/policy; live AWS apply deferred to account bootstrap) |

## Exit criteria

- [x] Encrypted/versioned/locked/access-logged remote state design (bootstrap module); per-env keys
- [x] Multi-AZ VPC, private nodes, Flow Logs, managed EKS, IRSA, secrets encryption
- [x] GitHub OIDC role catalog with permissions boundaries; immutable encrypted ECR
- [x] Policy-as-code + IAM negative tests; Terraform fmt/validate
- [x] Scoped plan workflow (OIDC optional); no long-lived keys; no PR apply

## Deliverables

| Artifact | Path |
|---|---|
| Bootstrap | `infra/terraform/bootstrap/` |
| Modules | `infra/terraform/modules/{network,eks,ecr,kms,iam_github_oidc}/` |
| Env stacks | `infra/terraform/envs/{dev,staging,prod}/` |
| Tfvars examples | `infra/terraform/Data/*.tfvars.json` |
| Workflow | `.github/workflows/terraform.yml` |
| Architecture/cost | `docs/architecture/aws_platform.md` |
| Plan stub | `docs/evidence/release-d/phase-13-plan-stub.md` |

## Verify

```text
terraform -chdir=infra/terraform/envs/staging fmt -check
terraform -chdir=infra/terraform/envs/staging init -backend=false
terraform -chdir=infra/terraform/envs/staging validate
pytest -q tests/terraform
```

Local verify (2026-08-01): staging/dev/prod/bootstrap `validate` **pass**; `pytest -q tests/terraform` → **12 passed**.

Live `terraform plan` against AWS requires bootstrap + `vars.AWS_ROLE_TO_ASSUME` (OIDC). Until then, negative IAM proof remains design + workflow assertions (extends Phase 01).

## Notes

- Staging is reproducible from committed modules + `Data/staging.tfvars.json` once bucket names are replaced.
- State restore: enable S3 versioning (bootstrap) + DynamoDB PITR; restore prior state object then `terraform init`.
