variable "aws_region" {
  type        = string
  description = "AWS region for state and logging resources"
  default     = "us-east-1"
}

variable "project" {
  type        = string
  description = "Short project slug used in resource names"
  default     = "cifar-cnn"
}

variable "state_bucket_name" {
  type        = string
  description = "Globally unique S3 bucket name for Terraform remote state"
}

variable "lock_table_name" {
  type        = string
  description = "DynamoDB table name for Terraform state locking"
  default     = "cifar-cnn-terraform-locks"
}

variable "access_log_bucket_name" {
  type        = string
  description = "Globally unique S3 bucket for state-bucket access logs"
}
