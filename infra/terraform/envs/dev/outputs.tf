output "vpc_id" {
  value = module.network.vpc_id
}

output "private_subnet_ids" {
  value = module.network.private_subnet_ids
}

output "eks_cluster_name" {
  value = module.eks.cluster_name
}

output "eks_api_irsa_role_arn" {
  value = module.eks.api_irsa_role_arn
}

output "ecr_repository_url" {
  value = module.ecr.repository_url
}

output "ci_build_role_arn" {
  value = module.iam_github_oidc.ci_build_role_arn
}

output "ci_terraform_plan_role_arn" {
  value = module.iam_github_oidc.ci_terraform_plan_role_arn
}

output "ci_terraform_apply_role_arn" {
  value = module.iam_github_oidc.ci_terraform_apply_role_arn
}

output "kms_key_arn" {
  value = module.kms.key_arn
}
