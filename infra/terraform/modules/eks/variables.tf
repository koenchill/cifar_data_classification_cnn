variable "name" {
  type = string
}

variable "cluster_version" {
  type    = string
  default = "1.31"
}

variable "private_subnet_ids" {
  type = list(string)
}

variable "vpc_id" {
  type = string
}

variable "kms_key_arn" {
  type = string
}

variable "endpoint_public_access" {
  type        = bool
  description = "Public API endpoint; keep false for hardened staging/prod when possible"
  default     = false
}

variable "endpoint_private_access" {
  type    = bool
  default = true
}

variable "node_instance_types" {
  type    = list(string)
  default = ["t3.medium"]
}

variable "node_desired_size" {
  type    = number
  default = 2
}

variable "node_min_size" {
  type    = number
  default = 2
}

variable "node_max_size" {
  type    = number
  default = 4
}

variable "tags" {
  type    = map(string)
  default = {}
}
