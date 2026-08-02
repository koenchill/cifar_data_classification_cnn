terraform {
  required_version = ">= 1.5.0, < 2.0.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.80"
    }
  }

  # Bootstrap uses local state once, then stores subsequent state in the created bucket.
  # After first apply, migrate with: terraform init -migrate-state
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = var.project
      ManagedBy   = "terraform"
      Component   = "tf-bootstrap"
      Environment = "shared"
    }
  }
}
