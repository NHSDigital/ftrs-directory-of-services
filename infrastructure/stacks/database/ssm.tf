resource "aws_ssm_parameter" "dynamodb_backup_arns" {
  count = local.is_primary_environment ? 1 : 0

  name        = "/${var.project}/${var.environment}/dynamodb-tables-backup-arns"
  description = "The latest backup ARNs for the DynamoDB tables"
  type        = "String"
  value       = "TBC"
}
