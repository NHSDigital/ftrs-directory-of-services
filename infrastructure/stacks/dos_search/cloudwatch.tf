# CloudWatch resources for this stack.

resource "aws_cloudwatch_log_group" "waf_log_group" {
  # checkov:skip=CKV_AWS_158: Justification: Using AWS default encryption.
  # checkov:skip=CKV_AWS_338: Justification: Non-production do not require long term log retention.
  name              = "aws-waf-logs-${local.resource_prefix}-dos-search${local.workspace_suffix}"
  retention_in_days = var.waf_log_retention_days
}

# Allow AWS WAF log delivery service to write WAF logs to CloudWatch Logs.
resource "aws_cloudwatch_log_resource_policy" "dos_search_waf_log_group_policy" {
  policy_document = data.aws_iam_policy_document.dos_search_waf_log_group_policy_document.json
  policy_name     = "${local.resource_prefix}-dos-search-waf-log-group-policy${local.workspace_suffix}"
}
