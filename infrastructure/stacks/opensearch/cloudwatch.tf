resource "aws_cloudwatch_log_group" "osis_pipeline_cloudwatch_log_group" {
  # checkov:skip=CKV_AWS_158: TODO https://nhsd-jira.digital.nhs.uk/browse/FDOS-404
  name              = "${var.osis_pipeline_cloudwatch_log_group_name}-${var.environment}${local.workspace_suffix}"
  retention_in_days = var.osis_pipeline_log_retention_in_days
}
