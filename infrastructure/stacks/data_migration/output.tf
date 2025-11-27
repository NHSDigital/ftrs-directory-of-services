output "state_table_arn" {
  description = "ARN of the data migration state table"
  value       = module.state_table.dynamodb_table_arn
}

output "state_table_name" {
  description = "Name of the data migration state table"
  value       = "${local.resource_prefix}-state-table${local.workspace_suffix}"
}
