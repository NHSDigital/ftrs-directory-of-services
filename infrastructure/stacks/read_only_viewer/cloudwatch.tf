resource "aws_cloudwatch_log_group" "read_only_viewer_waf_log_group" {
  # checkov:skip=CKV_AWS_158: Temp suppression JIRA-445
  name              = "${var.read_only_viewer_log_group_name_prefix}${local.resource_prefix}-${var.read_only_viewer_log_group}${local.workspace_suffix}"
  retention_in_days = var.read_only_viewer_log_group_retention_days
  log_group_class   = var.read_only_viewer_log_group_class
  provider          = aws.us-east-1
}
