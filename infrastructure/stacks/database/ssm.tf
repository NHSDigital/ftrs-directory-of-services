resource "aws_ssm_parameter" "backup_arns" {
  name        = "/${local.resource_prefix}${local.workspace_suffix}/tables-backup-arns"
  description = "The latest backup ARNs for the DynamoDB tables"
  type        = "String"
  value       = "TBC"
}
