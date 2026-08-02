locals {
  oidc_provider_url = "token.actions.githubusercontent.com"
  repo_sub_prefix   = "repo:${var.github_org}/${var.github_repo}"
  # GitHub Actions OIDC root CA thumbprint (documented by GitHub/AWS).
  github_thumbprint = "6938fd4d98bab03faadb97b34396831e3780aea1"
}

resource "aws_iam_openid_connect_provider" "github" {
  url             = "https://${local.oidc_provider_url}"
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = [local.github_thumbprint]
  tags            = var.tags
}

# Boundary blocks privilege-escalation IAM mutations; does not grant admin.
resource "aws_iam_policy" "permissions_boundary" {
  name = "${var.name_prefix}-boundary"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "DenyPrivilegeEscalation"
        Effect = "Deny"
        Action = [
          "iam:CreateUser",
          "iam:CreateAccessKey",
          "iam:CreateLoginProfile",
          "iam:AttachUserPolicy",
          "iam:PutUserPolicy",
          "iam:UpdateLoginProfile",
          "iam:PassRole",
        ]
        Resource = "*"
      },
      {
        Sid    = "AllowNonAdminWorkload"
        Effect = "Allow"
        NotAction = [
          "organizations:*",
          "account:*",
          "iam:CreateRole",
          "iam:DeleteRole",
          "iam:AttachRolePolicy",
          "iam:PutRolePolicy",
          "iam:UpdateAssumeRolePolicy",
        ]
        Resource = "*"
      }
    ]
  })
  tags = var.tags
}

data "aws_iam_policy_document" "ci_build_assume" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRoleWithWebIdentity"]
    principals {
      type        = "Federated"
      identifiers = [aws_iam_openid_connect_provider.github.arn]
    }
    condition {
      test     = "StringEquals"
      variable = "${local.oidc_provider_url}:aud"
      values   = ["sts.amazonaws.com"]
    }
    condition {
      test     = "StringLike"
      variable = "${local.oidc_provider_url}:sub"
      values = [
        "${local.repo_sub_prefix}:ref:refs/heads/dev",
        "${local.repo_sub_prefix}:ref:refs/heads/main",
        "${local.repo_sub_prefix}:pull_request",
      ]
    }
  }
}

resource "aws_iam_role" "ci_build" {
  name                 = "${var.name_prefix}-ci-build"
  assume_role_policy   = data.aws_iam_policy_document.ci_build_assume.json
  permissions_boundary = aws_iam_policy.permissions_boundary.arn
  tags                 = merge(var.tags, { Role = "ci-build" })
}

resource "aws_iam_role_policy" "ci_build_ecr" {
  name = "${var.name_prefix}-ci-build-ecr"
  role = aws_iam_role.ci_build.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "EcrAuth"
        Effect   = "Allow"
        Action   = ["ecr:GetAuthorizationToken"]
        Resource = "*"
      },
      {
        Sid    = "EcrPushPull"
        Effect = "Allow"
        Action = [
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:PutImage",
          "ecr:InitiateLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload",
          "ecr:DescribeRepositories",
          "ecr:DescribeImages",
        ]
        Resource = [var.ecr_repository_arn]
      },
      {
        Sid    = "DenyTerraformApplySurfaces"
        Effect = "Deny"
        Action = [
          "eks:UpdateClusterConfig",
          "eks:CreateNodegroup",
          "eks:DeleteCluster",
          "eks:CreateCluster",
        ]
        Resource = ["*"]
      }
    ]
  })
}

data "aws_iam_policy_document" "ci_plan_assume" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRoleWithWebIdentity"]
    principals {
      type        = "Federated"
      identifiers = [aws_iam_openid_connect_provider.github.arn]
    }
    condition {
      test     = "StringEquals"
      variable = "${local.oidc_provider_url}:aud"
      values   = ["sts.amazonaws.com"]
    }
    condition {
      test     = "StringLike"
      variable = "${local.oidc_provider_url}:sub"
      values = [
        "${local.repo_sub_prefix}:ref:refs/heads/dev",
        "${local.repo_sub_prefix}:pull_request",
      ]
    }
  }
}

resource "aws_iam_role" "ci_terraform_plan" {
  name                 = "${var.name_prefix}-ci-terraform-plan"
  assume_role_policy   = data.aws_iam_policy_document.ci_plan_assume.json
  permissions_boundary = aws_iam_policy.permissions_boundary.arn
  tags                 = merge(var.tags, { Role = "ci-terraform-plan" })
}

resource "aws_iam_role_policy" "ci_plan" {
  name = "${var.name_prefix}-ci-plan"
  role = aws_iam_role.ci_terraform_plan.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "StateList"
        Effect   = "Allow"
        Action   = ["s3:ListBucket"]
        Resource = [var.state_bucket_arn]
        Condition = {
          StringLike = { "s3:prefix" = ["${var.state_key_prefix}*"] }
        }
      },
      {
        Sid      = "StateRead"
        Effect   = "Allow"
        Action   = ["s3:GetObject"]
        Resource = ["${var.state_bucket_arn}/${var.state_key_prefix}*"]
      },
      {
        Sid    = "LockTable"
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:DeleteItem",
          "dynamodb:DescribeTable",
        ]
        Resource = [var.lock_table_arn]
      },
      {
        Sid    = "DenyApplyMutations"
        Effect = "Deny"
        Action = [
          "s3:DeleteObject",
          "ec2:TerminateInstances",
          "eks:DeleteCluster",
          "eks:UpdateClusterConfig",
          "eks:CreateCluster",
        ]
        Resource = ["*"]
      }
    ]
  })
}

data "aws_iam_policy_document" "ci_apply_assume" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRoleWithWebIdentity"]
    principals {
      type        = "Federated"
      identifiers = [aws_iam_openid_connect_provider.github.arn]
    }
    condition {
      test     = "StringEquals"
      variable = "${local.oidc_provider_url}:aud"
      values   = ["sts.amazonaws.com"]
    }
    condition {
      test     = "StringLike"
      variable = "${local.oidc_provider_url}:sub"
      values = [
        "${local.repo_sub_prefix}:environment:terraform-apply-*",
      ]
    }
  }
}

resource "aws_iam_role" "ci_terraform_apply" {
  name                 = "${var.name_prefix}-ci-terraform-apply"
  assume_role_policy   = data.aws_iam_policy_document.ci_apply_assume.json
  permissions_boundary = aws_iam_policy.permissions_boundary.arn
  tags                 = merge(var.tags, { Role = "ci-terraform-apply" })
}

resource "aws_iam_role_policy" "ci_apply_state" {
  name = "${var.name_prefix}-ci-apply-state"
  role = aws_iam_role.ci_terraform_apply.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "StateRW"
        Effect = "Allow"
        Action = ["s3:GetObject", "s3:PutObject", "s3:ListBucket"]
        Resource = [
          var.state_bucket_arn,
          "${var.state_bucket_arn}/${var.state_key_prefix}*",
        ]
      },
      {
        Sid    = "LockTable"
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:DeleteItem",
          "dynamodb:DescribeTable",
        ]
        Resource = [var.lock_table_arn]
      }
    ]
  })
}
