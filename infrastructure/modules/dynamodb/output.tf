output "dynamodb_table_arn" {
  description = "Calls the dynamodb table arn"
  value       = module.dynamodb_table.dynamodb_table_arn
}
