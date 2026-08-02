output "state_bucket_name" {
  value       = aws_s3_bucket.state.bucket
  description = "Per-account Terraform state bucket (isolate keys per env)"
}

output "lock_table_name" {
  value = aws_dynamodb_table.locks.name
}

output "state_kms_key_arn" {
  value = aws_kms_key.state.arn
}

output "access_log_bucket_name" {
  value = aws_s3_bucket.access_logs.bucket
}

output "account_id" {
  value = data.aws_caller_identity.current.account_id
}
