resource "aws_cloudwatch_log_group" "read_only_viewer_waf_log_group" {
  name              = "${local.resource_prefix}-${var.read_only_viewer_log_group}${local.workspace_suffix}"
  retention_in_days = var.read_only_viewer_log_group_retention_days
  log_group_class   = var.read_only_viewer_log_group_class
}

resource "aws_cloudwatch_log_resource_policy" "read_only_viewer_waf_log_group_policy" {
  policy_document = data.aws_iam_policy_document.read_only_viewer_waf_log_group_policy_document.json
  policy_name     = "${local.resource_prefix}-${var.read_only_viewer_waf_web_acl_log_group_policy_name}${local.workspace_suffix}"
}

data "aws_iam_policy_document" "read_only_viewer_waf_log_group_policy_document" {
  version = "2012-10-17"
  statement {
    effect = "Allow"
    principals {
      identifiers = ["delivery.logs.amazonaws.com"]
      type        = "Service"
    }
    actions   = ["logs:CreateLogStream", "logs:PutLogEvents"]
    resources = ["${aws_cloudwatch_log_group.read_only_viewer_waf_log_group.arn}:*"]
    condition {
      test     = "ArnLike"
      values   = ["arn:aws:logs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:*"]
      variable = "aws:SourceArn"
    }
    condition {
      test     = "StringEquals"
      values   = [tostring(data.aws_caller_identity.current.account_id)]
      variable = "aws:SourceAccount"
    }
  }
}
