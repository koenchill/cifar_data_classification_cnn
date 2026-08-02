variable "name" {
  type = string
}

variable "cidr_block" {
  type    = string
  default = "10.40.0.0/16"
}

variable "az_count" {
  type    = number
  default = 3
}

variable "single_nat_gateway" {
  type        = bool
  description = "Cost control: one NAT for non-prod; prod should use false"
  default     = true
}

variable "tags" {
  type    = map(string)
  default = {}
}
