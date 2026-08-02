data "aws_caller_identity" "current" {}

locals {
  name_prefix = "${var.project}-${var.environment}"
  tags = {
    Project     = var.project
    Environment = var.environment
  }
  state_key_prefix = "envs/${var.environment}/"
  lock_table_arn   = "arn:aws:dynamodb:${var.aws_region}:${data.aws_caller_identity.current.account_id}:table/${var.lock_table_name}"
}

module "kms" {
  source = "../../modules/kms"
  name   = "${local.name_prefix}-platform"
  tags   = local.tags
}

module "network" {
  source             = "../../modules/network"
  name               = local.name_prefix
  cidr_block         = var.vpc_cidr
  single_nat_gateway = var.single_nat_gateway
  tags               = local.tags
}

module "ecr" {
  source          = "../../modules/ecr"
  repository_name = "${var.project}/${var.environment}/api"
  kms_key_arn     = module.kms.key_arn
  tags            = local.tags
}

module "eks" {
  source                 = "../../modules/eks"
  name                   = local.name_prefix
  cluster_version        = var.cluster_version
  private_subnet_ids     = module.network.private_subnet_ids
  vpc_id                 = module.network.vpc_id
  kms_key_arn            = module.kms.key_arn
  endpoint_public_access = var.endpoint_public_access
  node_instance_types    = var.node_instance_types
  node_desired_size      = var.node_desired_size
  tags                   = local.tags
}

module "iam_github_oidc" {
  source             = "../../modules/iam_github_oidc"
  name_prefix        = local.name_prefix
  github_org         = var.github_org
  github_repo        = var.github_repo
  ecr_repository_arn = module.ecr.repository_arn
  state_bucket_arn   = "arn:aws:s3:::${var.state_bucket_name}"
  state_key_prefix   = local.state_key_prefix
  lock_table_arn     = local.lock_table_arn
  tags               = local.tags
}
