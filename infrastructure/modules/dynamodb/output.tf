output "dynamodb_table_arn" {
  description = "Calls the dynamodb table arn"
  value       = module.dynamodb_table.dynamodb_table_arn
}

output "dynamodb_table_stream_arn" {
  description = "ARN of the DynamoDB table stream"
  value       = module.dynamodb_table.dynamodb_table_stream_arn
}
