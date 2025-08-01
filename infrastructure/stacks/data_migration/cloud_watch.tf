resource "aws_cloudwatch_log_group" "dms_log_group" {
  count = local.deploy_databases ? 1 : 0

  name              = "/aws/dms/${local.resource_prefix}-etl-replication-task"
  retention_in_days = var.cloudwatch_log_retention_days
}
