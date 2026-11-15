output "state_bucket_name" {
  description = "Use this bucket name in every other stack's backend config."
  value       = aws_s3_bucket.tfstate.bucket
}

output "account_id" {
  value = data.aws_caller_identity.current.account_id
}

output "region" {
  value = var.region
}
