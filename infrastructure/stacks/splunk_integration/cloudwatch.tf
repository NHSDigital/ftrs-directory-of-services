

resource "aws_cloudwatch_log_group" "firehose_error_log_group" {
  count = local.is_primary_environment ? 1 : 0
  # checkov:skip=CKV_AWS_158: Justification: Using AWS default encryption.
  name              = "${local.resource_prefix}-${var.firehose_error_log_group_name}"
  retention_in_days = var.firehose_logs_retention_in_days
}
