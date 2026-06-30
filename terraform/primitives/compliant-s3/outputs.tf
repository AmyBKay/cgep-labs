output "bucket_arn"  { value = aws_s3_bucket.vault.arn }
output "bucket_name" { value = aws_s3_bucket.vault.id }
output "encryption_algorithm" {
  value = tolist(aws_s3_bucket_server_side_encryption_configuration.vault.rule)[0].apply_server_side_encryption_by_default[0].sse_algorithm
}
