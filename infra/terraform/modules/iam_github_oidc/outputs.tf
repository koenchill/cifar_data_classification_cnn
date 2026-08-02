output "github_oidc_provider_arn" {
  value = aws_iam_openid_connect_provider.github.arn
}

output "ci_build_role_arn" {
  value = aws_iam_role.ci_build.arn
}

output "ci_terraform_plan_role_arn" {
  value = aws_iam_role.ci_terraform_plan.arn
}

output "ci_terraform_apply_role_arn" {
  value = aws_iam_role.ci_terraform_apply.arn
}

output "permissions_boundary_arn" {
  value = aws_iam_policy.permissions_boundary.arn
}
