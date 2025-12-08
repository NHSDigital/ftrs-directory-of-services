resource "aws_cloudwatch_log_group" "osis_pipeline_cloudwatch_log_group" {
  # checkov:skip=CKV_AWS_158: Justification: Using AWS default encryption.
  name              = "${var.osis_pipeline_cloudwatch_log_group_name}-${var.environment}${local.workspace_suffix}"
  retention_in_days = var.osis_pipeline_logs_retention_in_days
}
