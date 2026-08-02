# Terraform — AWS reference platform (Release D / Phase 13)

Per-environment stacks under `envs/{dev,staging,prod}`. **Do not share state keys across environments.**

## Layout

| Path | Purpose |
|---|---|
| `bootstrap/` | Encrypted versioned S3 state + DynamoDB lock + access logs (apply once) |
| `modules/` | `network`, `eks`, `ecr`, `kms`, `iam_github_oidc` |
| `envs/*` | Environment roots (isolated backend keys) |
| `Data/*.tfvars.json` | Non-secret variable examples for each env |

## Bootstrap (once per account)

```text
cd infra/terraform/bootstrap
terraform init
terraform apply \
  -var="state_bucket_name=REPLACE-UNIQUE-cifar-cnn-tf-state" \
  -var="access_log_bucket_name=REPLACE-UNIQUE-cifar-cnn-tf-logs"
```

## Staging plan/apply (OIDC; no long-lived keys)

```text
cd infra/terraform/envs/staging
cp backend.hcl.example backend.hcl   # edit bucket/key
cp terraform.tfvars.example terraform.tfvars
terraform init -backend-config=backend.hcl
terraform plan -var-file=../../Data/staging.tfvars.json
# apply only via GitHub Environment terraform-apply-staging
```

## Local verify (no AWS credentials)

```text
terraform -chdir=infra/terraform/envs/staging fmt -check
terraform -chdir=infra/terraform/envs/staging init -backend=false
terraform -chdir=infra/terraform/envs/staging validate
```

## Continuity (Release E)

- State bucket is versioned + KMS-encrypted with access logs (bootstrap module).
- Restore targets and procedures: `docs/runbooks/continuity-restore.md`.
- Live account apply remains an ORR bootstrap step before production traffic.

## Forbidden

- Wildcard IAM admin without exception
- Public node exposure / open SG ingress without documented exception
- Long-lived AWS keys in CI
- Shared state object keys across environments
