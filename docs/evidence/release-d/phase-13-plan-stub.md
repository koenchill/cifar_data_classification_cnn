# Phase 13 Plan Artifact Stub

A live `terraform plan` output is produced by `.github/workflows/terraform.yml` job `oidc-plan-staging` when repository variable `AWS_ROLE_TO_ASSUME` is set after bootstrap.

Until AWS account bootstrap completes, this stub records the intended plan surfaces:

| Resource class | Module | Notes |
|---|---|---|
| VPC / subnets / NAT / Flow Logs | `modules/network` | Private node subnets |
| CMK | `modules/kms` | EKS secrets + ECR |
| EKS + node group + IRSA | `modules/eks` | Private endpoint default |
| ECR immutable | `modules/ecr` | Scan on push |
| GitHub OIDC roles | `modules/iam_github_oidc` | plan/apply/build separation |

**No apply** is performed from pull requests.
