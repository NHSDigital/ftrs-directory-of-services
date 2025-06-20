resource "aws_cloudwatch_log_group" "osis_pipeline_cloudwatch_log_group" {
  name              = "${var.osis_pipeline_cloudwatch_log_group_name}-${var.environment}${local.workspace_suffix}"
  retention_in_days = var.osis_pipeline_log_retention_in_days
}
