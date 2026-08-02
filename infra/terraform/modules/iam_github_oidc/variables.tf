variable "name_prefix" {
  type = string
}

variable "github_org" {
  type = string
}

variable "github_repo" {
  type = string
}

variable "ecr_repository_arn" {
  type = string
}

variable "state_bucket_arn" {
  type        = string
  description = "State bucket ARN for plan/apply roles (env-scoped prefix enforced in policies)"
}

variable "state_key_prefix" {
  type        = string
  description = "Allowed state object prefix for this environment, e.g. envs/staging/"
}

variable "lock_table_arn" {
  type = string
}

variable "tags" {
  type    = map(string)
  default = {}
}
