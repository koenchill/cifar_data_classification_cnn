# AWS Platform Assumptions (Phase 13 / Release D)

## Honesty

This is the **reference EKS platform** design. Local Docker (Phase 12) is not equivalent.

## Topology

- Multi-AZ VPC (`/16`) with public subnets (NAT only) and private subnets (EKS nodes)
- VPC Flow Logs → CloudWatch Logs
- Managed EKS with secrets encryption (CMK), private API endpoint default
- IRSA role for `cifar-cnn/api` service account (wired in Phase 14)
- Immutable, scanned, KMS-encrypted ECR repository per environment
- GitHub OIDC roles: `ci-build`, `ci-terraform-plan`, `ci-terraform-apply` (environment-gated)

## State isolation

| Env | State key |
|---|---|
| staging | `envs/staging/terraform.tfstate` |
| prod | `envs/prod/terraform.tfstate` |
| dev | `envs/dev/terraform.tfstate` |

Bootstrap creates a single encrypted/versioned bucket + DynamoDB lock table; **keys remain per-env**.

## Cost assumptions (staging)

| Item | Assumption |
|---|---|
| NAT | Single NAT gateway (`single_nat_gateway=true`) |
| Nodes | 2× `t3.medium` managed node group |
| Control plane | 1 EKS cluster |
| Logs | 30-day Flow Log + control-plane log retention |
| Rough monthly | ~USD 150–250 excluding data transfer (region-dependent) |

Prod defaults to per-AZ NAT and larger nodes — re-estimate before apply.

## Apply path

1. Bootstrap once  
2. Plan via OIDC (`ci-terraform-plan`)  
3. Apply only from protected GitHub Environment `terraform-apply-*` using `ci-terraform-apply`  
4. Never store long-lived AWS keys in GitHub secrets for routine apply
