resource "aws_cloudwatch_log_group" "read_only_viewer_waf_log_group" {
  # checkov:skip=CKV_AWS_158: TODO https://nhsd-jira.digital.nhs.uk/browse/FDOS-404
  count             = local.is_primary_environment ? 1 : 0
  name              = "${var.read_only_viewer_log_group_name_prefix}${local.resource_prefix}-${var.read_only_viewer_log_group}"
  retention_in_days = var.read_only_viewer_log_group_retention_days
  log_group_class   = var.read_only_viewer_log_group_class
  provider          = aws.us-east-1
}
